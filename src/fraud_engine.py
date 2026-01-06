import pyodbc
import pandas as pd
import time

# Configuración
CONN_STRING = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=LOCALHOST;"
    r"DATABASE=BankGuard;"
    r"Trusted_Connection=yes;"
)

class MotorDeFraude:
    def __init__(self, connection_string):
        # Guardamos la cadena de conexión en una variable de la instancia
        self.conn_string = connection_string
        print("Inicializando motor de fraude. Esperando transacciones")
        print("Presioná Ctrl + C para frenarlo.")

    def obtenerPendientes(self):
        conn = pyodbc.connect(self.conn_string)

        # Con pandas leemos la query usando la conexión y pedimos que devuelva un DataFrame
        query = "SELECT * FROM Transacciones WHERE estado = 'PENDIENTE'"
        df = pd.read_sql(query, conn)
        
        # Cerramos conexión (pandas no siempre la cierra)
        conn.close()

        return df # Devuelve el DataFrame
    
    def procesarLote(self):
        # Trae la tabla de pendientes
        df_pendientes = self.obtenerPendientes()

        # Si la tabla está vacía no hace nada
        if df_pendientes.empty:
            print("No hay nuevas transacciones")
            return # Para no gastar recursos
        
        # Nueva conexión para UPDATE/INSERT
        conn = pyodbc.connect(self.conn_string)
        cursor = conn.cursor()

        # Itera fila por fila del DataFrame (index = número de fila, row = los datos de esa fila, ejemplo: monto)
        for index, row in df_pendientes.iterrows():
            transaccion_id = row['transaccion_id']
            monto = row['monto']

            if monto > 500000:
                nuevo_estado = 'RECHAZADA' # Probable fraude
                print(f"Fraude detectado: Transacción ID: {transaccion_id} de {monto}.")
                audit_sql = ("INSERT INTO Auditoria_Fraude (transaccion_id, regla_activada, riesgo_score, accion_tomada, detalle) " \
                "VALUES (?, ?, ?, ?, ?)")
                cursor.execute(audit_sql, (transaccion_id, 'MONTO_ALTO', 90, 'BLOQUEO', f'Monto ${monto} excede limite'))
            else:
                nuevo_estado = 'APROBADA'

            cursor.execute("UPDATE Transacciones SET estado = ? WHERE transaccion_id = ?", (nuevo_estado, transaccion_id))   

        conn.commit()
        conn.close()

    def iniciarVigilancia(self):
        while True:
            self.procesarLote()
            time.sleep(5) # Espera 5 segundos antes de volver a buscar

if __name__ == "__main__":
    # Instancia el objeto y lo ponemos a trabajar
    motor = MotorDeFraude(CONN_STRING)
    motor.procesarLote()