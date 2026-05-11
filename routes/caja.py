from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from database import get_db_connection, col_cierres
from auth.decorators import empleado

BOGOTA = timezone(timedelta(hours=-5))

caja_bp = Blueprint('caja', __name__, url_prefix='/api/caja')


@caja_bp.route('/resumen-hoy', methods=['GET'])
@jwt_required()
@empleado
def resumen_hoy():
    """Devuelve el resumen de ventas del día actual y si ya hay cierre."""
    hoy = datetime.now(BOGOTA).strftime('%Y-%m-%d')

    # Verificar si ya hay cierre hoy
    cierre_existente = col_cierres.find_one({"fecha": hoy}, {"_id": 0})
    if cierre_existente:
        return jsonify({"ya_cerrado": True, "cierre": cierre_existente})

    conn = get_db_connection()
    facturas = conn.execute('''
        SELECT f.id_factura, f.total, f.fecha, f.cc_cliente,
               u.nombre AS nombre_cliente
        FROM factura f
        LEFT JOIN cliente  c ON f.cc_cliente = c.cc_cliente
        LEFT JOIN usuario  u ON c.id_usuario = u.id_usuario
        WHERE DATE(f.fecha) = ?
        ORDER BY f.fecha DESC
    ''', (hoy,)).fetchall()

    # Producto más vendido hoy
    productos_vendidos = conn.execute('''
        SELECT p.nombre, SUM(fd.cantidad) AS total_vendido
        FROM factura_detalle fd
        JOIN factura  f ON fd.id_factura      = f.id_factura
        JOIN producto p ON fd.id_producto = p.codigo_producto
        WHERE DATE(f.fecha) = ?
        GROUP BY fd.id_producto
        ORDER BY total_vendido DESC
        LIMIT 1
    ''', (hoy,)).fetchone()

    conn.close()

    total_recaudado    = sum(f['total'] or 0 for f in facturas)
    producto_top       = dict(productos_vendidos) if productos_vendidos else None

    return jsonify({
        "ya_cerrado":        False,
        "fecha":             hoy,
        "total_ventas":      len(facturas),
        "total_recaudado":   total_recaudado,
        "producto_mas_vendido": producto_top,
        "facturas":          [dict(f) for f in facturas]
    })


@caja_bp.route('/cerrar', methods=['POST'])
@jwt_required()
@empleado
def cerrar_caja():
    """Ejecuta el cierre de caja del día."""
    claims = get_jwt()
    hoy    = datetime.now(BOGOTA).strftime('%Y-%m-%d')

    if col_cierres.find_one({"fecha": hoy}):
        return jsonify({"error": "Ya se realizó el cierre de caja de hoy"}), 400

    conn = get_db_connection()
    facturas = conn.execute('''
        SELECT f.id_factura, f.total, f.fecha, f.cc_cliente,
               u.nombre AS nombre_cliente
        FROM factura f
        LEFT JOIN cliente  c ON f.cc_cliente = c.cc_cliente
        LEFT JOIN usuario  u ON c.id_usuario = u.id_usuario
        WHERE DATE(f.fecha) = ?
        ORDER BY f.fecha DESC
    ''', (hoy,)).fetchall()

    productos_vendidos = conn.execute('''
        SELECT p.nombre, SUM(fd.cantidad) AS total_vendido
        FROM factura_detalle fd
        JOIN factura  f ON fd.id_factura      = f.id_factura
        JOIN producto p ON fd.id_producto = p.codigo_producto
        WHERE DATE(f.fecha) = ?
        GROUP BY fd.id_producto
        ORDER BY total_vendido DESC
        LIMIT 1
    ''', (hoy,)).fetchone()

    conn.close()

    total_recaudado = sum(f['total'] or 0 for f in facturas)
    producto_top    = dict(productos_vendidos) if productos_vendidos else None

    documento = {
        "fecha":                 hoy,
        "hora_cierre":           datetime.now(BOGOTA).isoformat(),
        "cerrado_por":           claims.get('nombre', 'desconocido'),
        "rol":                   claims.get('rol'),
        "total_ventas":          len(facturas),
        "total_recaudado":       total_recaudado,
        "producto_mas_vendido":  producto_top,
        "detalle_ventas":        [dict(f) for f in facturas]
    }

    col_cierres.insert_one(documento)
    documento.pop('_id', None)

    return jsonify({"message": "Cierre de caja realizado exitosamente", "cierre": documento}), 201


@caja_bp.route('/historial', methods=['GET'])
@jwt_required()
@empleado
def historial_cierres():
    """Lista todos los cierres anteriores."""
    cierres = list(col_cierres.find({}, {"_id": 0}).sort("fecha", -1))
    return jsonify(cierres)