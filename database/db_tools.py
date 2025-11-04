import sqlite3
from langchain_core.tools import tool

DB_NAME = "inventario.db" # Asegúrate de que coincida con init_db.py

@tool
def consultar_stock(nombre_producto: str) -> str:
    """Usa esta herramienta para obtener la cantidad de stock actual de un producto por su nombre y su ubicación."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_actual, ubicacion FROM productos WHERE nombre = ?", (nombre_producto,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        stock, ubicacion = resultado
        return f"El stock actual de '{nombre_producto}' es {stock}. Se encuentra en la ubicación: {ubicacion}."
    return f"Error: Producto '{nombre_producto}' no encontrado en el inventario."

@tool
def actualizar_stock(nombre_producto: str, delta_cantidad: int) -> str:
    """
    Usa esta herramienta para AÑADIR o RESTAR stock de un producto.
    Si recibes unidades, 'delta_cantidad' es positivo. Si vendes/restas, es negativo.
    """
    if delta_cantidad == 0:
        return "Advertencia: La cantidad de actualización es cero. No se realizó ningún cambio."
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Obtener ID del producto antes de la actualización
    cursor.execute("SELECT id_producto FROM productos WHERE nombre = ?", (nombre_producto,))
    producto_id_result = cursor.fetchone()
    if not producto_id_result:
        conn.close()
        return f"Error: No se pudo actualizar. Producto '{nombre_producto}' no encontrado."
    
    producto_id = producto_id_result[0]

    # 2. Actualizar stock (Transacción principal)
    cursor.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id_producto = ?", (delta_cantidad, producto_id))
    
    # 3. Registrar el movimiento (Auditoría)
    tipo = 'ENTRADA' if delta_cantidad > 0 else 'SALIDA'
    cursor.execute("INSERT INTO movimientos (id_producto, tipo_movimiento, cantidad) VALUES (?, ?, ?)", 
                   (producto_id, tipo, abs(delta_cantidad)))
    
    # 4. Obtener el nuevo stock para confirmar (NLG)
    cursor.execute("SELECT stock_actual FROM productos WHERE id_producto = ?", (producto_id,))
    nuevo_stock = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    accion = "añadido" if delta_cantidad > 0 else "reducido"
    return f"Inventario actualizado: Se han {accion} {abs(delta_cantidad)} unidades de '{nombre_producto}'. El nuevo stock es {nuevo_stock}."