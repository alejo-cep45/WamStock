import sqlite3
from datetime import datetime, timezone, timedelta

BOGOTA = timezone(timedelta(hours=-5))

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from database import get_db_connection, col_movimientos, col_facturas_det
from auth.decorators import tendero, empleado

facturas_bp = Blueprint('facturas', __name__, url_prefix='/api/facturas')


@facturas_bp.route('', methods=['GET'])
@jwt_required()
@empleado
def get_facturas():
    conn = get_db_connection()
    facturas = conn.execute('''
        SELECT f.id_factura, f.cc_cliente, u.nombre AS nombre_cliente,
               f.fecha, f.total
        FROM factura f
        LEFT JOIN cliente  c ON f.cc_cliente = c.cc_cliente
        LEFT JOIN usuario  u ON c.id_usuario = u.id_usuario
        ORDER BY f.fecha DESC
    ''').fetchall()

    result = []
    for f in facturas:
        detalles = conn.execute('''
            SELECT fd.cantidad, fd.precio_unitario, fd.subtotal,
                   p.codigo_producto, p.nombre AS nombre_producto
            FROM factura_detalle fd
            JOIN producto p ON fd.id_producto = p.codigo_producto
            WHERE fd.id_factura = ?
        ''', (f['id_factura'],)).fetchall()
        row = dict(f)
        row['items'] = [dict(d) for d in detalles]
        result.append(row)

    conn.close()
    return jsonify(result)


@facturas_bp.route('/<int:id_factura>', methods=['GET'])
@jwt_required()
@empleado
def get_factura(id_factura):
    conn = get_db_connection()
    f = conn.execute('''
        SELECT f.id_factura, f.cc_cliente, u.nombre AS nombre_cliente,
               f.fecha, f.total
        FROM factura f
        LEFT JOIN cliente  c ON f.cc_cliente = c.cc_cliente
        LEFT JOIN usuario  u ON c.id_usuario = u.id_usuario
        WHERE f.id_factura = ?
    ''', (id_factura,)).fetchone()

    if f is None:
        conn.close()
        return jsonify({"error": "Factura no encontrada"}), 404

    detalles = conn.execute('''
        SELECT fd.cantidad, fd.precio_unitario, fd.subtotal,
               p.codigo_producto, p.nombre AS nombre_producto
        FROM factura_detalle fd
        JOIN producto p ON fd.id_producto = p.codigo_producto
        WHERE fd.id_factura = ?
    ''', (id_factura,)).fetchall()

    conn.close()
    row = dict(f)
    row['items'] = [dict(d) for d in detalles]
    return jsonify(row)


@facturas_bp.route('', methods=['POST'])
@jwt_required()
@empleado
def create_factura():
    """
    Body: {
      "cc_cliente": 1001,          (opcional)
      "items": [
        { "id_producto": 1, "cantidad": 2 },
        { "id_producto": 2, "cantidad": 1 }
      ]
    }
    """
    data = request.get_json()
    if not data or not data.get('items'):
        return jsonify({"error": "Se requiere al menos un item"}), 400

    claims     = get_jwt()
    cc_cliente = data.get('cc_cliente')
    items      = data['items']

    conn   = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar stock y calcular total
        total = 0
        items_detalle = []
        for item in items:
            prod = conn.execute(
                'SELECT nombre, precio, stock FROM producto WHERE codigo_producto = ?',
                (item['id_producto'],)
            ).fetchone()

            if prod is None:
                return jsonify({"error": f"Producto {item['id_producto']} no existe"}), 404

            cantidad = item.get('cantidad', 1)
            if prod['stock'] < cantidad:
                return jsonify({"error": f"Stock insuficiente para '{prod['nombre']}' (disponible: {prod['stock']})"}), 400

            subtotal = prod['precio'] * cantidad
            total   += subtotal
            items_detalle.append({
                "id_producto":     item['id_producto'],
                "nombre":          prod['nombre'],
                "cantidad":        cantidad,
                "precio_unitario": prod['precio'],
                "subtotal":        subtotal
            })

        # Crear factura
        fecha_bogota = datetime.now(BOGOTA).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            'INSERT INTO factura (cc_cliente, total, fecha) VALUES (?,?,?)',
            (cc_cliente, total, fecha_bogota)
        )
        new_id = cursor.lastrowid

        # Insertar detalles y descontar stock
        for item in items_detalle:
            cursor.execute('''
                INSERT INTO factura_detalle (id_factura, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?,?,?,?,?)
            ''', (new_id, item['id_producto'], item['cantidad'], item['precio_unitario'], item['subtotal']))

            cursor.execute(
                'UPDATE producto SET stock = stock - ? WHERE codigo_producto = ?',
                (item['cantidad'], item['id_producto'])
            )

        conn.commit()

        # Log MongoDB
        try:
            col_movimientos.insert_one({
                "tipo":           "venta",
                "id_factura":     new_id,
                "cliente":        cc_cliente,
                "items":          items_detalle,
                "total":          total,
                "registrado_por": claims.get('nombre', 'desconocido'),
                "rol":            claims.get('rol'),
                "fecha":          datetime.now(BOGOTA).isoformat()
            })
            col_facturas_det.insert_one({
                "id_factura":     new_id,
                "fecha_venta":    datetime.now(BOGOTA).isoformat(),
                "cliente_cc":     cc_cliente,
                "items":          items_detalle,
                "total":          total,
                "registrado_por": claims.get('nombre', 'desconocido'),
                "rol":            claims.get('rol'),
            })
        except Exception:
            pass

    except sqlite3.IntegrityError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()

    return jsonify({"id_factura": new_id, "total": total}), 201


@facturas_bp.route('/<int:id_factura>', methods=['DELETE'])
@jwt_required()
@tendero
def delete_factura(id_factura):
    conn   = get_db_connection()
    cursor = conn.cursor()

    # Restaurar stock antes de eliminar
    detalles = conn.execute(
        'SELECT id_producto, cantidad FROM factura_detalle WHERE id_factura = ?',
        (id_factura,)
    ).fetchall()

    for d in detalles:
        cursor.execute(
            'UPDATE producto SET stock = stock + ? WHERE codigo_producto = ?',
            (d['cantidad'], d['id_producto'])
        )

    cursor.execute('DELETE FROM factura_detalle WHERE id_factura = ?', (id_factura,))
    cursor.execute('DELETE FROM factura WHERE id_factura = ?', (id_factura,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Factura no encontrada"}), 404
    return jsonify({"message": "Factura eliminada y stock restaurado"})