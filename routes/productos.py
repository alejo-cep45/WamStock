import sqlite3
from datetime import datetime, timezone, timedelta

BOGOTA = timezone(timedelta(hours=-5))

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from database import get_db_connection, col_movimientos, col_alertas
from auth.decorators import tendero, empleado
from config import Config

productos_bp = Blueprint('productos', __name__, url_prefix='/api/productos')


@productos_bp.route('', methods=['GET'])
@jwt_required()
@empleado
def get_productos():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM producto').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@productos_bp.route('/<int:codigo>', methods=['GET'])
@jwt_required()
@empleado
def get_producto(codigo):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM producto WHERE codigo_producto = ?', (codigo,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(dict(row))


@productos_bp.route('', methods=['POST'])
@jwt_required()
@empleado
def create_producto():
    data = request.get_json()
    if not data or 'codigo_producto' not in data or 'nombre' not in data:
        return jsonify({"error": "Se requieren 'codigo_producto' y 'nombre'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO producto (codigo_producto, nombre, precio, stock, nit_proveedor)
            VALUES (?,?,?,?,?)
        ''', (data['codigo_producto'], data['nombre'],
              data.get('precio'), data.get('stock', 0), data.get('nit_proveedor')))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()
    return jsonify({"codigo_producto": data['codigo_producto']}), 201


@productos_bp.route('/<int:codigo>', methods=['PUT'])
@jwt_required()
@empleado
def update_producto(codigo):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacio"}), 400
    campos, valores = [], []
    for f in ('nombre', 'precio', 'stock', 'nit_proveedor'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if not campos:
        return jsonify({"error": "Sin campos validos"}), 400
    valores.append(codigo)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE producto SET {', '.join(campos)} WHERE codigo_producto = ?", valores)
    conn.commit()
    updated = cursor.rowcount
    if updated > 0:
        claims = get_jwt()
        try:
            col_movimientos.insert_one({
                "tipo":           "actualizacion_producto",
                "producto":       codigo,
                "datos":          data,
                "modificado_por": claims.get('nombre', 'desconocido'),
                "rol":            claims.get('rol'),
                "fecha":          datetime.now(BOGOTA).isoformat()
            })
            if 'stock' in data and data['stock'] <= Config.STOCK_MINIMO:
                producto_actual = conn.execute(
                    'SELECT nombre FROM producto WHERE codigo_producto = ?', (codigo,)
                ).fetchone()
                col_alertas.insert_one({
                    "codigo_producto": codigo,
                    "nombre_producto": producto_actual['nombre'] if producto_actual else "desconocido",
                    "stock_actual":    data['stock'],
                    "umbral":          Config.STOCK_MINIMO,
                    "modificado_por":  claims.get('nombre', 'desconocido'),
                    "fecha":           datetime.now(BOGOTA).isoformat()
                })
        except Exception:
            print("Mongo fallo pero SQL sigue funcionando")
    conn.close()
    if updated == 0:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"message": "Producto actualizado correctamente"})


@productos_bp.route('/<int:codigo>', methods=['DELETE'])
@jwt_required()
@tendero
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


@productos_bp.route('/<int:codigo>/historial', methods=['GET'])
@jwt_required()
@empleado
def get_historial_producto(codigo):
    conn = get_db_connection()
    producto = conn.execute(
        'SELECT * FROM producto WHERE codigo_producto = ?', (codigo,)
    ).fetchone()
    conn.close()
    if producto is None:
        return jsonify({"error": "Producto no encontrado"}), 404
    logs = list(col_movimientos.find({"producto": codigo}, {"_id": 0}))
    return jsonify({"producto": dict(producto), "historial": logs})