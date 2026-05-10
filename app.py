
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from config import Config

from auth.routes       import auth_bp
from routes.roles      import roles_bp
from routes.usuarios   import usuarios_bp
from routes.clientes   import clientes_bp
from routes.proveedores import proveedores_bp
from routes.productos  import productos_bp
from routes.facturas   import facturas_bp
from routes.logs       import logs_bp

from auth.routes        import auth_bp
from routes.roles       import roles_bp
from routes.usuarios    import usuarios_bp
from routes.clientes    import clientes_bp
from routes.proveedores import proveedores_bp
from routes.productos   import productos_bp
from routes.facturas    import facturas_bp
from routes.logs        import logs_bp
 
 
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    JWTManager(app)
 

    app.register_blueprint(auth_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(logs_bp)
 
    @app.route('/')
    def index():
        return render_template('login.html')
 
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
 
    @app.route('/productos')
    def vista_productos():
        return render_template('productos.html')
 
    @app.route('/ventas')
    def vista_ventas():
        return render_template('ventas.html')
 
    @app.route('/facturas')
    def vista_facturas():
        return render_template('facturas.html')
 
    @app.route('/clientes')
    def vista_clientes():
        return render_template('clientes.html')
 
    @app.route('/proveedores')
    def vista_proveedores():
        return render_template('proveedores.html')
 
    @app.route('/usuarios')
    def vista_usuarios():
        return render_template('usuarios.html')
 
    @app.route('/logs')
    def vista_logs():
        return render_template('logs.html')
 
    return app
 
 
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)


# ── MongoDB ───────────────────────────────────────────────────────────────────





# ── Flask & JWT ───────────────────────────────────────────────────────────────



# ── Helpers ───────────────────────────────────────────────────────────────────









# ── AUTH ──────────────────────────────────────────────────────────────────────







# ── ROLES ─────────────────────────────────────────────────────────────────────



# ── USUARIO ───────────────────────────────────────────────────────────────────


# ── CLIENTE ───────────────────────────────────────────────────────────────────



# ── PROVEEDOR ─────────────────────────────────────────────────────────────────



# ── PRODUCTO ──────────────────────────────────────────────────────────────────



# ── FACTURA ───────────────────────────────────────────────────────────────────



# ── LOGS MONGO ────────────────────────────────────────────────────────────────




