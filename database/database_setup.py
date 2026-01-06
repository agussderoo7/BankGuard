import pyodbc
import time

# --- CONFIGURACIÓN DE CONEXIÓN ---
# Ajustá SERVER según el nombre de tu PC o instancia SQL
# Si usás Windows Authentication, Trusted_Connection=yes es la clave.
CONN_STRING = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=LOCALHOST;"  # O probá con .\SQLEXPRESS si falla
    r"DATABASE=BankGuard;"
    r"Trusted_Connection=yes;"
)

def probar_conexion():
    print("Intentando conectar a BankGuard en SQL Server...")
    
    try:
        # Conectar
        conn = pyodbc.connect(CONN_STRING)
        cursor = conn.cursor()
        print("Conexión exitosa al Motor de Base de Datos")

        # Verificar que las tablas existen (Query al sistema)
        print("📂 Verificando esquema de tablas...")
        cursor.execute("SELECT name FROM sys.tables")
        tablas = [row[0] for row in cursor.fetchall()]
        
        tablas_esperadas = ['Clientes', 'Transacciones', 'Dispositivos_Seguros', 'Auditoria_Fraude']
        
        todas_ok = True
        for tabla in tablas_esperadas:
            if tabla in tablas:
                print(f"   - Tabla found: {tabla} [OK]")
            else:
                print(f"   - ALERTA: No se encuentra la tabla {tabla}")
                todas_ok = False
        
        if todas_ok:
            print("\n TODO LISTO. La infraestructura está operativa.")
            print("   Próximo paso: Generar datos falsos (Seeding).")
        else:
            print("\n Faltan tablas. Revisá tu script SQL en SSMS.")

        conn.close()

    except Exception as e:
        print("\n ERROR CRÍTICO DE CONEXIÓN:")
        print(e)
        print("\nRevisar si el nombre de tu SERVER es correcto en el string de conexión.")

if __name__ == "__main__":
    probar_conexion()