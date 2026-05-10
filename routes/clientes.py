import sqlite3
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from database import get_db_connection
from auth.decorators import tendero, empleado

clientes_bp = Blueprint('clientes', __name__, url_prefix='/api/clientes')

@clientes_bp.route('', methods=['GET'])
@jwt_required()
@empleado
def get_clientes():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT c.cc_cliente, u.nombre, u.email
        FROM cliente c JOIN usuario u ON c.id_usuario = u.id_usuario
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@clientes_bp.route('/<int:cc_cliente>', methods=['GET'])
@jwt_required()
@empleado
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

@clientes_bp.route('', methods=['POST'])
@jwt_required()
@tendero
def create_cliente():
    data = request.get_json()
    if not data or 'cc_cliente' not in data or 'id_usuario' not in data:
        return jsonify({"error": "Se requieren 'cc_cliente' e 'id_usuario'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO cliente (cc_cliente, id_usuario) VALUES (?,?)',
                       (data['cc_cliente'], data['id_usuario']))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()
    return jsonify({"cc_cliente": data['cc_cliente']}), 201

@clientes_bp.route('/<int:cc_cliente>', methods=['PUT'])
@jwt_required()
@tendero
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

@clientes_bp.route('/<int:cc_cliente>', methods=['DELETE'])
@jwt_required()
@tendero
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
