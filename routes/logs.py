from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database import col_movimientos, col_sesiones, col_alertas, col_facturas_det
from auth.decorators import tendero, empleado
 
logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')



@logs_bp.route('', methods=['GET'])
@jwt_required()
@empleado
def get_logs():
    logs = list(col_movimientos.find({}, {"_id": 0}))
    return jsonify(logs)

@logs_bp.route('/sesiones', methods=['GET'])
@jwt_required()
@tendero
def get_sesiones():
    sesiones = list(col_sesiones.find({}, {"_id": 0}))
    return jsonify(sesiones)

@logs_bp.route('/alertas-stock', methods=['GET'])
@jwt_required()
@empleado
def get_alertas_stock():
    alertas = list(col_alertas.find({}, {"_id": 0}))
    return jsonify(alertas)

@logs_bp.route('/facturas-detalle', methods=['GET'])
@jwt_required()
@empleado
def get_facturas_detalle():
    detalle = list(col_facturas_det.find({}, {"_id": 0}))
    return jsonify(detalle)

@logs_bp.route('/facturas-detalle/<int:id_factura>', methods=['GET'])
@jwt_required()
@empleado
def get_factura_detalle(id_factura):
    doc = col_facturas_det.find_one({"id_factura": id_factura}, {"_id": 0})
    if doc is None:
        return jsonify({"error": "Detalle no encontrado"}), 404
    return jsonify(doc)