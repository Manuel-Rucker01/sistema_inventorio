import sqlite3
from difflib import get_close_matches # Para buscar similitud

DB_NAME = "inventario.db" # Asegúrate de que coincida con init_db.py

# --- Herramientas de CONSULTA (Consulta Stock y Similitud) ---

def buscar_similitud(nombre_producto: str) -> str:
    """Usa esta herramienta cuando un producto no se encuentra. Devuelve una lista de nombres de productos similares."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Obtener TODOS los nombres de productos
    cursor.execute("SELECT nombre FROM productos")
    todos_nombres = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Usar difflib para encontrar sugerencias (cortar a 5 sugerencias con un umbral de 0.6)
    sugerencias = get_close_matches(nombre_producto, todos_nombres, n=5, cutoff=0.6)

    if sugerencias:
        sugerencias_str = ", ".join(sugerencias)
        return f"SUGERENCIAS_ENCONTRADAS: '{sugerencias_str}'. Pregúntale al usuario si se refiere a alguno de estos productos."
    return "SUGERENCIAS_NO_ENCONTRADAS: No se encontraron productos similares. La única opción es crear uno nuevo."

def consultar_stock(nombre_producto: str) -> str:
    """Usa esta herramienta para obtener el stock, ubicación y COSTO UNITARIO de un producto."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # MODIFICACIÓN: Seleccionar el nuevo campo costo_unitario
    cursor.execute("SELECT stock_actual, ubicacion, costo_unitario FROM productos WHERE nombre = ?", (nombre_producto,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        stock, ubicacion, costo = resultado
        # MODIFICACIÓN: Incluir el coste en la respuesta (NLG)
        return f"El stock actual de '{nombre_producto}' es {stock}. Se encuentra en: {ubicacion}. El costo unitario es ${costo:.2f}."
        
    # Si no se encuentra, sugerimos al LLM que llame a la herramienta de similitud
    return f"PRODUCTO_NO_ENCONTRADO: Producto '{nombre_producto}' no encontrado en el inventario. Deberías usar la herramienta buscar_similitud."

# --- Herramientas de CREACIÓN y ACTUALIZACIÓN ---

def crear_producto(nombre_producto: str, stock_inicial: int = 0, costo_unitario: float = 0.0, ubicacion: str = "PENDIENTE") -> str:
    """
    Usa esta herramienta para añadir un producto COMPLETAMENTE NUEVO al inventario. 
    Se requiere 'nombre_producto'. Acepta stock_inicial y costo_unitario (float).
    """
    if not nombre_producto:
        return "Error: No se puede crear un producto sin un nombre válido."
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # MODIFICACIÓN: Añadir costo_unitario a la inserción
        cursor.execute("""
            INSERT INTO productos (nombre, stock_actual, costo_unitario, ubicacion) 
            VALUES (?, ?, ?, ?)
        """, (nombre_producto, stock_inicial, costo_unitario, ubicacion))
        conn.commit()
        return f"ÉXITO_CREACIÓN: Producto '{nombre_producto}' creado con stock inicial de {stock_inicial} y costo unitario de ${costo_unitario:.2f}."
    except sqlite3.IntegrityError:
        return f"Error: Ya existe un producto con el nombre '{nombre_producto}'."
    except Exception as e:
        return f"Error al crear el producto: {e}"
    finally:
        conn.close()

def actualizar_stock(nombre_producto: str, delta_cantidad: int) -> str:
    """
    Usa esta herramienta para AÑADIR o RESTAR stock de un producto EXISTENTE.
    Si el producto no existe, debes primero sugerir similitudes o usar crear_producto.
    """
    if delta_cantidad == 0:
        return "Advertencia: La cantidad de actualización es cero. No se realizó ningún cambio."
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Obtener ID del producto (y verificar existencia)
    cursor.execute("SELECT id_producto FROM productos WHERE nombre = ?", (nombre_producto,))
    producto_id_result = cursor.fetchone()
    if not producto_id_result:
        conn.close()
        # Si no se encuentra, sugerimos al LLM que llame a la herramienta de similitud
        return f"PRODUCTO_NO_ENCONTRADO: Producto '{nombre_producto}' no encontrado. Debes usar buscar_similitud o crear_producto."
    
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