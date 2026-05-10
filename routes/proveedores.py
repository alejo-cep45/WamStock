import sqlite3
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from database import get_db_connection
from auth.decorators import tendero, empleado
 
proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/api/proveedores')

@proveedores_bp.route('', methods=['GET'])
@jwt_required()
@empleado
def get_proveedores():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM proveedor').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@proveedores_bp.route('/<int:nit>', methods=['GET'])
@jwt_required()
@empleado
def get_proveedor(nit):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM proveedor WHERE nit_proveedor = ?', (nit,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Proveedor no encontrado"}), 404
    return jsonify(dict(row))

@proveedores_bp.route('', methods=['POST'])
@jwt_required()
@tendero
def create_proveedor():
    data = request.get_json()
    if not data or 'nit_proveedor' not in data or 'nombre' not in data:
        return jsonify({"error": "Se requieren 'nit_proveedor' y 'nombre'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO proveedor (nit_proveedor, nombre, contacto) VALUES (?,?,?)',
                       (data['nit_proveedor'], data['nombre'], data.get('contacto')))
        conn.commit()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        conn.close()
    return jsonify({"nit_proveedor": data['nit_proveedor']}), 201

@proveedores_bp.route('/<int:nit>', methods=['PUT'])
@jwt_required()
@tendero
def update_proveedor(nit):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacio"}), 400
    campos, valores = [], []
    for f in ('nombre', 'contacto'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if not campos:
        return jsonify({"error": "Sin campos validos"}), 400
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

@proveedores_bp.route('/<int:nit>', methods=['DELETE'])
@jwt_required()
@tendero
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
