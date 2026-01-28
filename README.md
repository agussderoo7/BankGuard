# 🛡️ BankGuard: Sistema de Detección de Fraude en Tiempo Real

**BankGuard** es un motor de seguridad transaccional diseñado para detectar, auditar y bloquear operaciones fraudulentas bancarias en tiempo real. Utiliza un enfoque híbrido de reglas de negocio (Velocidad y Monto) y visualización de datos en vivo.

---

## 🚀 Características Principales

### Motor de Decisión Híbrido:
- **Regla de Monto:** Bloqueo automático de transacciones superiores a límites definidos (>$500k).
- **Regla de Velocidad:** Detección de "Ráfagas" (>3 transacciones por usuario en <1 minuto).
### Dashboard en Tiempo Real:
Interfaz desarrollada en Streamlit para monitoreo de KPIs, alertas y dispersión de datos.
### Ingeniería de Datos:
- Integración **SQLAlchemy** para ingesta masiva de datos (Lectura optimizada).
- Conexión **PyODBC** para escritura transaccional de alta velocidad.
- Auditoría persistente en **SQL Server** para análisis forense.
### Simulación de Estrés:
Generador de datos sintéticos incluido para realizar pruebas de carga y validar la latencia del motor.

---

## 🛠️ Tecnologías

* **Lenguaje:** Python 3.11
* **Base de Datos:** Microsoft SQL Server
* **Librerías Clave:**
    * `pandas` (Manipulación de DataFrames)
    * `sqlalchemy` (Gestión de Conexiones)
    * `plotly` (Visualización Interactiva)
    * `streamlit` (Frontend Web)
    * `pyodbc` (Driver SQL)

---

## ⚙️ Arquitectura del Proyecto

El sistema sigue el principio de **Separación de Responsabilidades**:

```text
BankGuard/
├── src/
│   ├── fraud_engine.py    # Procesa reglas y bloquea fraudes.
│   └── ...
├── database/
│   ├── seed_data.py       # Crea tráfico simulado.
│   └── setup.sql          # Scripts de creación de tablas.
├── app.py                 # Dashboard visual para el analista.
└── README.md

```
---

## 💻 Instalación y Uso

### Prerrequisitos
Para ejecutar este proyecto localmente, se necesita:
* [Python 3.10+](https://www.python.org/downloads/)
* [SQL Server](https://www.microsoft.com/es-es/sql-server/sql-server-downloads) (Developer o Express edition)
* [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 1. Clonar el repositorio
```bash
git clone [https://github.com/agussderoo7/BankGuard.git](https://github.com/agussderoo7/BankGuard.git)
cd BankGuard
```

### 2. Configurar la Base de Datos
- Abre SQL Server Management Studio (SSMS).
- Ejecuta el script ubicado en database/setup.sql. Esto creará la base de datos BankGuard y las tablas necesarias.
- Opcional: Verifica que la variable SERVER en los archivos .py coincida con el nombre de tu servidor local.

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```
### 4. Ejecutar el Sistema (Modo Demo)
Para simular el entorno de producción, se recomienda abrir 3 terminales simultáneas en VS Code:

Terminal A: Dashboard (Inicia la interfaz web de monitoreo).
```bash
streamlit run app.py
```

Terminal B: Motor de Fraude (Inicia el servicio de vigilancia que procesa las reglas en tiempo real).
```bash
python src/fraud_engine.py
```

Terminal C: Generador de Tráfico (Inyecta transacciones sintéticas para estresar el sistema y probar las reglas).
```bash
python database/seed_data.py
```

---

## 🔮 Próximos Pasos
El desarrollo de BankGuard es continuo. Estas son las próximas funcionalidades planificadas:
- [ ]  Machine Learning: Implementación de Isolation Forest para detección de anomalías no supervisadas (patrones desconocidos).
- [ ]  Dockerización: Containerización de la app y la base de datos para despliegue ágil.
- [ ]  Sistema de Alertas: Integración con API de Email o Slack para notificaciones críticas instantáneas.

**Autor:** Agustin De Roo

**Contacto:** agustinderoo05@gmail.com | www.linkedin.com/in/agustinderoo
