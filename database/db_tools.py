import sqlite3
from difflib import get_close_matches 

DB_NAME = "inventario.db" 

# --- Herramientas de CONSULTA y SIMILITUD ---

def buscar_similitud(nombre_producto: str) -> str:
    """
    HERRAMIENTA DE DIAGNÓSTICO. Utilízala SOLAMENTE cuando una consulta de stock o actualización de producto 
    devuelve PRODUCTO_NO_ENCONTRADO.
    
    Esta herramienta busca nombres de productos similares en la base de datos para sugerir correcciones al usuario.
    
    :param nombre_producto: El nombre exacto que el usuario introdujo.
    :return: SUGERENCIAS_ENCONTRADAS o SUGERENCIAS_NO_ENCONTRADAS.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM productos")
    todos_nombres = [row[0] for row in cursor.fetchall()]
    conn.close()

    sugerencias = get_close_matches(nombre_producto, todos_nombres, n=5, cutoff=0.6)

    if sugerencias:
        sugerencias_str = ", ".join(sugerencias)
        return f"SUGERENCIAS_ENCONTRADAS: '{sugerencias_str}'. Pregúntale al usuario si se refiere a alguno de estos productos."
    return "SUGERENCIAS_NO_ENCONTRADAS: No se encontraron productos similares. La única opción es crear uno nuevo."

def consultar_stock(nombre_producto: str) -> str:
    """
    HERRAMIENTA DE CONSULTA. Utilízala cuando el usuario pregunte por la cantidad, ubicación o costo de un producto EXISTENTE.
    
    Esta herramienta devuelve: stock_actual, ubicación y costo_unitario.
    
    :param nombre_producto: Nombre completo del producto a consultar.
    :return: El estado del inventario o la etiqueta PRODUCTO_NO_ENCONTRADO.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_actual, ubicacion, costo_unitario FROM productos WHERE nombre = ?", (nombre_producto,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        stock, ubicacion, costo = resultado
        return f"El stock actual de '{nombre_producto}' es {stock}. Se encuentra en: {ubicacion}. El costo unitario es ${costo:.2f}."
        
    return f"PRODUCTO_NO_ENCONTRADO: Producto '{nombre_producto}' no encontrado en el inventario. Deberías usar la herramienta buscar_similitud."

# --- Herramientas de CREACIÓN y ACTUALIZACIÓN ---

def crear_producto(nombre_producto: str, stock_inicial: int = 0, costo_unitario: float = 0.0, ubicacion: str = "PENDIENTE") -> str:
    """
    HERRAMIENTA DE CREACIÓN. Utilízala cuando el usuario indique que quiere agregar un producto TOTALMENTE NUEVO después de que 
    la herramienta 'buscar_similitud' haya fallado o el usuario haya dicho 'NO' a las sugerencias.
    
    ARGUMENTOS REQUERIDOS: nombre_producto, stock_inicial (unidades que se acaban de recibir) y costo_unitario.
    
    :param nombre_producto: Nombre exacto del nuevo producto.
    :param stock_inicial: Cantidad de unidades a ingresar inicialmente (debe ser extraído del input del usuario).
    :param costo_unitario: Costo de compra por unidad (debe ser extraído del input del usuario).
    :param ubicacion: Ubicación física (opcional, usar 'PENDIENTE' si no se menciona).
    :return: ÉXITO_CREACIÓN o Error.
    """
    if not nombre_producto:
        return "Error: No se puede crear un producto sin un nombre válido."
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
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
    HERRAMIENTA DE ACTUALIZACIÓN. Utilízala cuando el usuario quiera añadir (delta > 0) o restar (delta < 0) unidades de un producto EXISTENTE. 
    
    SI EL PRODUCTO NO EXISTE, la herramienta fallará. Debes manejar el error llamando a buscar_similitud.
    
    :param nombre_producto: Nombre completo del producto a modificar.
    :param delta_cantidad: Número de unidades a sumar (positivo) o restar (negativo).
    :return: Confirmación de inventario con el nuevo stock o la etiqueta PRODUCTO_NO_ENCONTRADO.
    """
    if delta_cantidad == 0:
        return "Advertencia: La cantidad de actualización es cero. No se realizó ningún cambio."
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_producto FROM productos WHERE nombre = ?", (nombre_producto,))
    producto_id_result = cursor.fetchone()
    if not producto_id_result:
        conn.close()
        return f"PRODUCTO_NO_ENCONTRADO: Producto '{nombre_producto}' no encontrado. Debes usar buscar_similitud o crear_producto."
    
    producto_id = producto_id_result[0]

    cursor.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id_producto = ?", (delta_cantidad, producto_id))
    
    tipo = 'ENTRADA' if delta_cantidad > 0 else 'SALIDA'
    cursor.execute("INSERT INTO movimientos (id_producto, tipo_movimiento, cantidad) VALUES (?, ?, ?)", 
                   (producto_id, tipo, abs(delta_cantidad)))
    
    cursor.execute("SELECT stock_actual FROM productos WHERE id_producto = ?", (producto_id,))
    nuevo_stock = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    accion = "añadido" if delta_cantidad > 0 else "reducido"
    return f"Inventario actualizado: Se han {accion} {abs(delta_cantidad)} unidades de '{nombre_producto}'. El nuevo stock es {nuevo_stock}."