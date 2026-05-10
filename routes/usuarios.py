import sqlite3
import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from database import get_db_connection
from auth.decorators import tendero
 
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')
 
@usuarios_bp.route('', methods=['GET'])
@jwt_required()
@tendero
def get_usuarios():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT u.id_usuario, u.nombre, u.email, r.nombre_rol
        FROM usuario u LEFT JOIN roles r ON u.id_rol = r.id_rol
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@usuarios_bp.route('/<int:id_usuario>', methods=['GET'])
@jwt_required()
@tendero
def get_usuario(id_usuario):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT u.id_usuario, u.nombre, u.email, r.nombre_rol
        FROM usuario u LEFT JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.id_usuario = ?
    ''', (id_usuario,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(dict(row))

@usuarios_bp.route('', methods=['POST'])
@jwt_required()
@tendero
def create_usuario():
    data = request.get_json()
    if not data or 'nombre' not in data or 'email' not in data:
        return jsonify({"error": "Se requieren 'nombre' y 'email'"}), 400
    hashed = None
    if data.get('contrasena'):
        hashed = bcrypt.hashpw(data['contrasena'].encode(), bcrypt.gensalt()).decode()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO usuario (nombre, email, contrasena, id_rol) VALUES (?,?,?,?)',
            (data['nombre'], data['email'], hashed, data.get('id_rol'))
        )
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        return jsonify({"error": f"Email ya registrado: {e}"}), 409
    finally:
        conn.close()
    return jsonify({"id_usuario": new_id, "nombre": data['nombre'], "email": data['email']}), 201

@usuarios_bp.route('/<int:id_usuario>', methods=['PUT'])
@jwt_required()
@tendero
def update_usuario(id_usuario):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo vacio"}), 400
    campos, valores = [], []
    for f in ('nombre', 'email', 'id_rol'):
        if f in data:
            campos.append(f'{f} = ?')
            valores.append(data[f])
    if 'contrasena' in data:
        campos.append('contrasena = ?')
        valores.append(bcrypt.hashpw(data['contrasena'].encode(), bcrypt.gensalt()).decode())
    if not campos:
        return jsonify({"error": "Sin campos validos"}), 400
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

@usuarios_bp.route('/<int:id_usuario>', methods=['DELETE'])
@jwt_required()
@tendero
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