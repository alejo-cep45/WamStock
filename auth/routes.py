import bcrypt
from datetime import datetime, timezone, timedelta

BOGOTA = timezone(timedelta(hours=-5))

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from database import get_db_connection, col_sesiones

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Body: { "email": "...", "contrasena": "..." }
    El rol se obtiene de la BD, no lo manda el cliente.
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'contrasena')):
        return jsonify({"error": "Se requieren 'email' y 'contrasena'"}), 400

    conn = get_db_connection()
    row = conn.execute('''
        SELECT u.id_usuario, u.nombre, u.email, u.contrasena, r.nombre_rol
        FROM usuario u
        JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.email = ?
    ''', (data['email'],)).fetchone()
    conn.close()

    if row is None or row['contrasena'] is None:
        return jsonify({"error": "Credenciales invalidas"}), 401

    if not bcrypt.checkpw(data['contrasena'].encode(), row['contrasena'].encode()):
        return jsonify({"error": "Credenciales invalidas"}), 401

    token = create_access_token(
        identity=str(row['id_usuario']),
        additional_claims={
            "rol":    row['nombre_rol'],
            "nombre": row['nombre'],
            "email":  row['email']
        }
    )

    try:
        col_sesiones.insert_one({
            "email":  row['email'],
            "nombre": row['nombre'],
            "rol":    row['nombre_rol'],
            "ip":     request.remote_addr,
            "fecha":  datetime.now(BOGOTA).isoformat()
        })
    except Exception:
        pass

    return jsonify({
        "access_token": token,
        "rol":    row['nombre_rol'],
        "nombre": row['nombre']
    })


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    claims = get_jwt()
    return jsonify({
        "id":     get_jwt_identity(),
        "rol":    claims.get('rol'),
        "nombre": claims.get('nombre'),
        "email":  claims.get('email')
    })