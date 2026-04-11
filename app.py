import sqlite3
from flask import Flask, jsonify, request
from datetime import datetime
from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:admin@cluster0.fjdxl7l.mongodb.net/?appName=Cluster0")
db = client['inventario']
coleccion = db["movimientos_log"]

app = Flask(__name__)
DATABASE = 'inventario.db'

def get_db_connection():
    conn = sqlite3.connect(
        DATABASE,
        timeout=10,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode=WAL") 
    return conn


# USUARIO


@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM usuario').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/usuarios/<int:id_usuario>', methods=['GET'])
def get_usuario(id_usuario):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM usuario WHERE id_usuario = ?', (id_usuario,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(dict(row))

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuario (nombre, email) VALUES (?, ?)',
                       (data['nombre'], data.get('email')))
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        return jsonify({"error": f"Email ya registrado: {e}"}), 409
    finally:
        conn.close()
    return jsonify({"id_usuario": new_id, "nombre": data['nombre'], "email": data.get('email')}), 201

@app.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def update_usuario(id_usuario):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío"}), 400
    campos, valores = [], []
    for f in ('nombre', 'email'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if not campos:
        return jsonify({"error": "Sin campos válidos"}), 400
    valores.append(id_usuario)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE usuario SET {', '.join(campos)} WHERE id_usuario = ?", valores)
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"message": "Usuario actualizado correctamente"})

@app.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def delete_usuario(id_usuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuario WHERE id_usuario = ?', (id_usuario,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"message": "Usuario eliminado exitosamente"})


# CLIENTE


@app.route('/clientes', methods=['GET'])
def get_clientes():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT c.cc_cliente, u.nombre, u.email
        FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/clientes/<int:cc_cliente>', methods=['GET'])
def get_cliente(cc_cliente):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT c.cc_cliente, c.id_usuario, u.nombre, u.email
        FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario
        WHERE c.cc_cliente = ?
    ''', (cc_cliente,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify(dict(row))

@app.route('/clientes', methods=['POST'])
def create_cliente():
    data = request.get_json()
    if not data or 'cc_cliente' not in data or 'id_usuario' not in data:
        return jsonify({"error": "Se requieren 'cc_cliente' e 'id_usuario'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO cliente (cc_cliente, id_usuario) VALUES (?, ?)',
                       (data['cc_cliente'], data['id_usuario']))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()
    return jsonify({"cc_cliente": data['cc_cliente']}), 201

@app.route('/clientes/<int:cc_cliente>', methods=['PUT'])
def update_cliente(cc_cliente):
    data = request.get_json()
    if not data or 'id_usuario' not in data:
        return jsonify({"error": "Se requiere 'id_usuario'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE cliente SET id_usuario = ? WHERE cc_cliente = ?',
                   (data['id_usuario'], cc_cliente))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify({"message": "Cliente actualizado correctamente"})

@app.route('/clientes/<int:cc_cliente>', methods=['DELETE'])
def delete_cliente(cc_cliente):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cliente WHERE cc_cliente = ?', (cc_cliente,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify({"message": "Cliente eliminado exitosamente"})




@app.route('/empleados', methods=['GET'])
def get_empleados():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT e.id_empleado, u.nombre, u.email
        FROM empleado e JOIN usuario u ON e.id_usuario = u.id_usuario
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/empleados/<int:id_empleado>', methods=['GET'])
def get_empleado(id_empleado):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT e.id_empleado, e.id_usuario, u.nombre, u.email
        FROM empleado e JOIN usuario u ON e.id_usuario = u.id_usuario
        WHERE e.id_empleado = ?
    ''', (id_empleado,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Empleado no encontrado"}), 404
    return jsonify(dict(row))

@app.route('/empleados', methods=['POST'])
def create_empleado():
    data = request.get_json()
    if not data or 'contrasena' not in data or 'id_usuario' not in data:
        return jsonify({"error": "Se requieren 'contrasena' e 'id_usuario'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO empleado (contrasena, id_usuario) VALUES (?, ?)',
                       (data['contrasena'], data['id_usuario']))
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()
    return jsonify({"id_empleado": new_id}), 201

@app.route('/empleados/<int:id_empleado>', methods=['PUT'])
def update_empleado(id_empleado):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío"}), 400
    campos, valores = [], []
    for f in ('contrasena', 'id_usuario'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if not campos:
        return jsonify({"error": "Sin campos válidos"}), 400
    valores.append(id_empleado)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE empleado SET {', '.join(campos)} WHERE id_empleado = ?", valores)
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Empleado no encontrado"}), 404
    return jsonify({"message": "Empleado actualizado correctamente"})

@app.route('/empleados/<int:id_empleado>', methods=['DELETE'])
def delete_empleado(id_empleado):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM empleado WHERE id_empleado = ?', (id_empleado,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Empleado no encontrado"}), 404
    return jsonify({"message": "Empleado eliminado exitosamente"})



@app.route('/tenderos', methods=['GET'])
def get_tenderos():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT t.id_tendero, u.nombre, u.email
        FROM tendero t JOIN usuario u ON t.id_usuario = u.id_usuario
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/tenderos/<int:id_tendero>', methods=['GET'])
def get_tendero(id_tendero):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT t.id_tendero, t.id_usuario, u.nombre, u.email
        FROM tendero t JOIN usuario u ON t.id_usuario = u.id_usuario
        WHERE t.id_tendero = ?
    ''', (id_tendero,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Tendero no encontrado"}), 404
    return jsonify(dict(row))

@app.route('/tenderos', methods=['POST'])
def create_tendero():
    data = request.get_json()
    if not data or 'contrasena' not in data or 'id_usuario' not in data:
        return jsonify({"error": "Se requieren 'contrasena' e 'id_usuario'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO tendero (contrasena, id_usuario) VALUES (?, ?)',
                       (data['contrasena'], data['id_usuario']))
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()
    return jsonify({"id_tendero": new_id}), 201

@app.route('/tenderos/<int:id_tendero>', methods=['PUT'])
def update_tendero(id_tendero):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío"}), 400
    campos, valores = [], []
    for f in ('contrasena', 'id_usuario'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if not campos:
        return jsonify({"error": "Sin campos válidos"}), 400
    valores.append(id_tendero)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE tendero SET {', '.join(campos)} WHERE id_tendero = ?", valores)
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Tendero no encontrado"}), 404
    return jsonify({"message": "Tendero actualizado correctamente"})

@app.route('/tenderos/<int:id_tendero>', methods=['DELETE'])
def delete_tendero(id_tendero):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tendero WHERE id_tendero = ?', (id_tendero,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Tendero no encontrado"}), 404
    return jsonify({"message": "Tendero eliminado exitosamente"})



@app.route('/proveedores', methods=['GET'])
def get_proveedores():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM proveedor').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/proveedores/<int:nit>', methods=['GET'])
def get_proveedor(nit):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM proveedor WHERE nit_proveedor = ?', (nit,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    return jsonify(dict(row))

@app.route('/proveedores', methods=['POST'])
def create_proveedor():
    data = request.get_json()
    if not data or 'nit_proveedor' not in data or 'nombre' not in data:
        return jsonify({"error": "Se requieren 'nit_proveedor' y 'nombre'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO proveedor (nit_proveedor, nombre, contacto) VALUES (?, ?, ?)',
                       (data['nit_proveedor'], data['nombre'], data.get('contacto')))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()
    return jsonify({"nit_proveedor": data['nit_proveedor']}), 201

@app.route('/proveedores/<int:nit>', methods=['PUT'])
def update_proveedor(nit):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío"}), 400
    campos, valores = [], []
    for f in ('nombre', 'contacto'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if not campos:
        return jsonify({"error": "Sin campos válidos"}), 400
    valores.append(nit)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE proveedor SET {', '.join(campos)} WHERE nit_proveedor = ?", valores)
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    return jsonify({"message": "Proveedor actualizado correctamente"})

@app.route('/proveedores/<int:nit>', methods=['DELETE'])
def delete_proveedor(nit):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM proveedor WHERE nit_proveedor = ?', (nit,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    return jsonify({"message": "Proveedor eliminado exitosamente"})




@app.route('/productos', methods=['GET'])
def get_productos():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM producto').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/productos/<int:codigo>', methods=['GET'])
def get_producto(codigo):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM producto WHERE codigo_producto = ?', (codigo,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(dict(row))

@app.route('/productos', methods=['POST'])
def create_producto():
    data = request.get_json()
    if not data or 'codigo_producto' not in data or 'nombre' not in data:
        return jsonify({"error": "Se requieren 'codigo_producto' y 'nombre'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO producto (codigo_producto, nombre, precio, stock, nit_proveedor)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['codigo_producto'], data['nombre'],
              data.get('precio'), data.get('stock', 0), data.get('nit_proveedor')))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()
    return jsonify({"codigo_producto": data['codigo_producto']}), 201

@app.route('/productos/<int:codigo>', methods=['PUT'])
def update_producto(codigo):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío"}), 400
    campos, valores = [], []
    for f in ('nombre', 'precio', 'stock', 'nit_proveedor'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if not campos:
        return jsonify({"error": "Sin campos válidos"}), 400
    valores.append(codigo)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE producto SET {', '.join(campos)} WHERE codigo_producto = ?", valores)
    conn.commit()
    updated = cursor.rowcount
    if updated > 0:
        try:
            coleccion.insert_one({
                "tipo": "actualizacion_producto",
                "producto": codigo,
                "datos": data,
                "fecha": datetime.now().isoformat()
            })
        except:
            print("Mongo falló pero SQL sigue funcionando")
    conn.close()
    if updated == 0:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"message": "Producto actualizado correctamente"})

@app.route('/productos/<int:codigo>', methods=['DELETE'])
def delete_producto(codigo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM producto WHERE codigo_producto = ?', (codigo,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"message": "Producto eliminado exitosamente"})

@app.route('/productos/<int:codigo>/historial', methods=['GET'])
def get_historial_producto(codigo):
    conn = get_db_connection()
    producto = conn.execute(
        'SELECT * FROM producto WHERE codigo_producto = ?',
        (codigo,)
    ).fetchone()
    conn.close()

    if producto is None:
        return jsonify({"error": "Producto no encontrado"}), 404

    logs = list(coleccion.find(
        {"producto": codigo},
        {"_id": 0}
    ))

    resultado = {
        "producto": dict(producto),
        "historial": logs
    }

    return jsonify(resultado)


@app.route('/facturas', methods=['GET'])
def get_facturas():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT f.id_factura, f.cc_cliente, u.nombre AS nombre_cliente,
               f.id_producto, p.nombre AS nombre_producto, p.precio, f.fecha
        FROM factura f
        JOIN cliente  c ON f.cc_cliente  = c.cc_cliente
        JOIN usuario  u ON c.id_usuario  = u.id_usuario
        JOIN producto p ON f.id_producto = p.codigo_producto
        ORDER BY f.fecha DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/facturas/<int:id_factura>', methods=['GET'])
def get_factura(id_factura):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT f.id_factura, f.cc_cliente, u.nombre AS nombre_cliente,
               f.id_producto, p.nombre AS nombre_producto, p.precio, f.fecha
        FROM factura f
        JOIN cliente  c ON f.cc_cliente  = c.cc_cliente
        JOIN usuario  u ON c.id_usuario  = u.id_usuario
        JOIN producto p ON f.id_producto = p.codigo_producto
        WHERE f.id_factura = ?
    ''', (id_factura,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Factura no encontrada"}), 404
    return jsonify(dict(row))

@app.route('/facturas', methods=['POST'])
def create_factura():
    data = request.get_json()

    if not data or 'cc_cliente' not in data or 'id_producto' not in data:
        return jsonify({"error": "Se requieren 'cc_cliente' e 'id_producto'"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO factura (cc_cliente, id_producto) VALUES (?, ?)',
            (data['cc_cliente'], data['id_producto'])
        )
        conn.commit()
        new_id = cursor.lastrowid

        coleccion.insert_one({
            "tipo": "venta",
            "id_factura": new_id,
            "cliente": data['cc_cliente'],
            "producto": data['id_producto'],
            "fecha": datetime.now().isoformat()
        })

    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409

    finally:
        conn.close()

    return jsonify({"id_factura": new_id}), 201

@app.route('/facturas/<int:id_factura>', methods=['PUT'])
def update_factura(id_factura):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacío"}), 400
    campos, valores = [], []
    for f in ('cc_cliente', 'id_producto'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if not campos:
        return jsonify({"error": "Sin campos válidos"}), 400
    valores.append(id_factura)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE factura SET {', '.join(campos)} WHERE id_factura = ?", valores)
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Factura no encontrada"}), 404
    return jsonify({"message": "Factura actualizada correctamente"})

@app.route('/facturas/<int:id_factura>', methods=['DELETE'])
def delete_factura(id_factura):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM factura WHERE id_factura = ?', (id_factura,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Factura no encontrada"}), 404
    return jsonify({"message": "Factura eliminada exitosamente"})

@app.route('/logs', methods=['GET'])
def get_logs():
    logs = list(coleccion.find({}, {"_id": 0}))
    return jsonify(logs)


if __name__ == '__main__':
    app.run(debug=True, port=5000)