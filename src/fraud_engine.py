import pyodbc
import pandas as pd
import time
from sqlalchemy import create_engine, text

# Para la conexión usamos SQLAlchemy para leer y pyodbc para escribir (más rápido para updates puntuales)
SERVER = 'LOCALHOST'
DATABASE = 'BankGuard'
# Connection String para SQLAlchemy (Lectura)
CONNECTION_STRING = f"mssql+pyodbc://{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
# Connection String para PyODBC (Escritura y chequeos rápidos)
RAW_CONN_STRING = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"

class MotorDeFraude:
    def __init__(self):
        # Motor para lecturas grandes (Pandas)
        self.engine = create_engine(CONNECTION_STRING)
        print("Inicio del motor de fraude avanzado")
        print("Vigilando: Montos Altos (> $500k) y Velocidad (3 transacciones/min)")
        print("Presioná Ctrl + C para detenerlo.")

    def obtenerPendientes(self):
        # Leemos con SQLAlchemy sin warning
        query = "SELECT * FROM Transacciones WHERE estado = 'PENDIENTE'"
        with self.engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        return df
    
    def checkVelocidad(self, cliente_id, fecha_actual_transaccion):
        # Consulta a la base de datos cuántas transacciones realizó el cliente en el último minuto
        conn = pyodbc.connect(RAW_CONN_STRING)
        cursor = conn.cursor()

        query = "SELECT COUNT(*) FROM Transacciones WHERE cliente_id = ? AND fecha_hora >= DATEADD(minute, -1, ?) AND fecha_hora <= ?"
        cursor.execute(query, (cliente_id, fecha_actual_transaccion, fecha_actual_transaccion))
        cantidad = cursor.fetchone()[0] # Trae el primer elemento
        conn.close()

        # Si hay 3 o más contando la actual, es sospechoso
        return cantidad >= 3

    def procesarLote(self):
        try:
            df_pendientes = self.obtenerPendientes()
        except Exception as e:
            print(f"Error de conexión: {e}")
            return

        if df_pendientes.empty:
            return 

        print(f"Analizando {len(df_pendientes)} transacciones nuevas")

        # Conexión para guardar los veredictos
        conn_update = pyodbc.connect(RAW_CONN_STRING)
        cursor = conn_update.cursor()

        for index, row in df_pendientes.iterrows():
            tx_id = row['transaccion_id']
            cliente_id = row['cliente_id']
            monto = row['monto']
            fecha = row['fecha_hora']
            
            es_fraude = False
            razon = ""
            regla = ""

            # Primera regla: monto excesivo
            if monto > 500000:
                es_fraude = True
                razon = f"Monto excesivo (${monto:,.0f})"
                regla = "MONTO_ALTO"

            # Segunda regla: velocidad
            if not es_fraude:
                if self.checkVelocidad(cliente_id, fecha):
                    es_fraude = True
                    razon = "Ráfaga de transacciones (>3 en 1 min)"
                    regla = "VELOCIDAD_ALTA"

            # Veredicto
            if es_fraude:
                nuevo_estado = 'RECHAZADA'
                print(f"BLOQUEADO Transacción {tx_id} | Cliente {cliente_id} | {razon}")
                
                # Guardar en Auditoría (Opcional porque, si falla, no rompe el programa)
                try:
                    audit_sql = """
                        INSERT INTO Auditoria_Fraude (transaccion_id, regla_activada, riesgo_score, accion_tomada, detalle)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    cursor.execute(audit_sql, (tx_id, regla, 95, 'BLOQUEO', razon))
                except:
                    pass # Si no existe la tabla auditoría, seguimos igual
            else:
                nuevo_estado = 'APROBADA'

            # Actualizar estado
            cursor.execute("UPDATE Transacciones SET estado = ? WHERE transaccion_id = ?", (nuevo_estado, tx_id))
            conn_update.commit()

        conn_update.close()
        print("Lote finalizado. Continuando vigilancia")

    def iniciarVigilancia(self):
        while True:
            self.procesarLote()
            time.sleep(5) # Espera 5 segundos antes de volver a buscar

if __name__ == "__main__":
    # Instancia el objeto y lo ponemos a trabajar
    motor = MotorDeFraude()
    motor.iniciarVigilancia()