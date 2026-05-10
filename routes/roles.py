import sqlite3
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from database import get_db_connection
from auth.decorators import tendero
 
roles_bp = Blueprint('roles', __name__, url_prefix='/api/roles')


@roles_bp.route('', methods=['GET'])
@jwt_required()
@tendero
def get_roles():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM roles').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@roles_bp.route('', methods=['POST'])
@jwt_required()
@tendero
def create_rol():
    data = request.get_json()
    if not data or 'nombre_rol' not in data:
        return jsonify({"error": "Se requiere 'nombre_rol'"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO roles (nombre_rol) VALUES (?)', (data['nombre_rol'],))
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error": "Ese rol ya existe"}), 409
    finally:
        conn.close()
    return jsonify({"id_rol": new_id, "nombre_rol": data['nombre_rol']}), 201

@roles_bp.route('/<int:id_rol>', methods=['DELETE'])
@jwt_required()
@tendero
def delete_rol(id_rol):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM roles WHERE id_rol = ?', (id_rol,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "Rol no encontrado"}), 404
    return jsonify({"message": "Rol eliminado exitosamente"})
