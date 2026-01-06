import pyodbc
import random
from faker import Faker

# Configuración (la misma que en database_setup)
CONN_STRING = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=LOCALHOST;" 
    r"DATABASE=BankGuard;"
    r"Trusted_Connection=yes;"
)

fake = Faker('es_AR') # Datos en español (Argentina)

def generar_datos_falsos():
    print("Iniciando generación de datos falsos en BankGuard")

    try:
        conn = pyodbc.connect(CONN_STRING)
        cursor = conn.cursor()

        # Generar 50 clientes
        print("Generando 50 clientes simulados")
        ids_clientes = []
        for i in range(50):
            nombre = fake.name()
            dni = str(fake.unique.random_number(digits = 8))
            email = fake.unique.email()
            score = random.randint(300, 850)

            cursor.execute("""
                INSERT INTO Clientes (nombre_completo, dni, email, score_crediticio, pais_residencia)
                values (?, ?, ?, ?, 'Argentina')
            """, (nombre, dni, email, score))
        
        conn.commit()

        # Asignar transacciones a los IDs generados
        cursor.execute("SELECT cliente_id FROM Clientes")
        ids_clientes = [row[0] for row in cursor.fetchall()]

        # Generar 200 transacciones
        print("Generando 200 transacciones")

        operaciones = ['TRANSFERENCIA', 'COMPRA', 'EXTRACCION']
        estados = ['PENDIENTE', 'APROBADA', 'RECHAZADA']

        for i in range(200):
            cliente_id = random.choice(ids_clientes)

            # Simulamos: 90% montos normales, 10% montos gigantes (posible fraude)
            if random.random() < 0.90:
                monto = round(random.uniform(100.00, 50000.00), 2)
            else:
                monto = round(random.uniform(500000.00, 2000000.00), 2)
            
            moneda = 'ARS'
            tipo = random.choice(operaciones)
            cbu_destino = fake.bban()
            ip = fake.ipv4()
            estado = 'PENDIENTE' # todas en pendiente para que el motor las procese
            cursor.execute("""
                INSERT INTO Transacciones (cliente_id, monto, moneda, tipo_operacion, destinatario_cbu, ip_origen, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)    
                """, (cliente_id, monto, moneda, tipo, cbu_destino, ip, estado))
        
        conn.commit()
        print("Sembrado completado. Base de datos lista con datos de prueba.")
        conn.close()
    
    except Exception as e:
        print(f"Error al sembrar los datos: {e}")

if __name__ == "__main__":
    generar_datos_falsos()