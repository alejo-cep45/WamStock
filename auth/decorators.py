from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def empleado(fn):
    """Permite acceso a empleados y tenderos (tendero hereda permisos de empleado)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('rol') not in ('empleado', 'tendero'):
            return jsonify({"error": "Se requiere rol empleado o superior"}), 403
        return fn(*args, **kwargs)
    return wrapper


def tendero(fn):
    """Permite acceso solo al tendero."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('rol') != 'tendero':
            return jsonify({"error": "Se requiere rol tendero"}), 403
        return fn(*args, **kwargs)
    return wrapper
