import sqlite3

DB_NAME = "inventario.db"

def init_db():
    """Crea la base de datos relacional y las tablas de productos/movimientos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Crear tabla de productos (Stock actual)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            stock_actual INTEGER NOT NULL DEFAULT 0,
            ubicacion TEXT,
            costo_unitario REAL NOT NULL DEFAULT 0.0 
        )
    """)
    
    # 2. Crear tabla de movimientos (para auditoría)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER,
            tipo_movimiento TEXT CHECK(tipo_movimiento IN ('ENTRADA', 'SALIDA')) NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    """)

    # ----------------------------------------------------
    # LÍNEAS ELIMINADAS: 
    # Ya no se insertan productos iniciales (Manzanas, Peras, Bananas)
    # ----------------------------------------------------
    
    conn.commit()
    conn.close()
    print(f"Base de datos relacional '{DB_NAME}' inicializada con éxito (VACÍA).")

# No hay bloque __main__, la función debe ser llamada desde agent_app.py