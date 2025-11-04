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
            ubicacion TEXT
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

    # 3. Insertar datos iniciales
    productos_iniciales = [
        ('Tornillo M4 x 10mm', 150, 'A1-03'),
        ('Martillo Bicolor 500g', 25, 'B2-01'),
        ('Taladro Perforador XL', 10, 'C1-05')
    ]
    cursor.executemany("INSERT OR IGNORE INTO productos (nombre, stock_actual, ubicacion) VALUES (?, ?, ?)", productos_iniciales)
    conn.commit()
    conn.close()
    print(f"Base de datos relacional '{DB_NAME}' inicializada con éxito.")

if __name__ == "__main__":
    init_db()