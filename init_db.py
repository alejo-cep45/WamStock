import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def setup_database():
    try:
        conn = sqlite3.connect('inventario.db')
        cursor = conn.cursor()

        print("Eliminando tablas anteriores...")
        cursor.executescript('''
            PRAGMA foreign_keys = OFF;
            DROP TABLE IF EXISTS factura_detalle;
            DROP TABLE IF EXISTS factura;
            DROP TABLE IF EXISTS producto;
            DROP TABLE IF EXISTS proveedor;
            DROP TABLE IF EXISTS cliente;
            DROP TABLE IF EXISTS usuario;
            DROP TABLE IF EXISTS roles;
            PRAGMA foreign_keys = ON;
        ''')

        print("Creando tablas...")

        cursor.execute('''
            CREATE TABLE roles (
                id_rol     INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_rol TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE usuario (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre     TEXT NOT NULL,
                email      TEXT NOT NULL UNIQUE,
                contrasena TEXT,
                id_rol     INTEGER,
                FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
            )
        ''')

        cursor.execute('''
            CREATE TABLE cliente (
                cc_cliente INTEGER PRIMARY KEY,
                id_usuario INTEGER NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            )
        ''')

        cursor.execute('''
            CREATE TABLE proveedor (
                nit_proveedor INTEGER PRIMARY KEY,
                nombre        TEXT NOT NULL,
                contacto      TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE producto (
                codigo_producto INTEGER PRIMARY KEY,
                nombre          TEXT NOT NULL,
                precio          REAL,
                stock           INTEGER DEFAULT 0,
                nit_proveedor   INTEGER,
                FOREIGN KEY (nit_proveedor) REFERENCES proveedor(nit_proveedor)
            )
        ''')

        cursor.execute('''
            CREATE TABLE factura (
                id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
                cc_cliente INTEGER,
                fecha      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total      REAL DEFAULT 0,
                FOREIGN KEY (cc_cliente) REFERENCES cliente(cc_cliente)
            )
        ''')

        cursor.execute('''
            CREATE TABLE factura_detalle (
                id_detalle      INTEGER PRIMARY KEY AUTOINCREMENT,
                id_factura      INTEGER NOT NULL,
                id_producto     INTEGER NOT NULL,
                cantidad        INTEGER NOT NULL DEFAULT 1,
                precio_unitario REAL NOT NULL,
                subtotal        REAL NOT NULL,
                FOREIGN KEY (id_factura)  REFERENCES factura(id_factura),
                FOREIGN KEY (id_producto) REFERENCES producto(codigo_producto)
            )
        ''')

        print("Insertando datos de prueba...")

        cursor.execute("INSERT INTO roles (nombre_rol) VALUES (?)", ("tendero",))
        cursor.execute("INSERT INTO roles (nombre_rol) VALUES (?)", ("empleado",))

        cursor.execute(
            "INSERT INTO usuario (nombre, email, contrasena, id_rol) VALUES (?,?,?,?)",
            ("Admin Tendero", "tendero@wamstock.com", hash_password("tendero123"), 1)
        )
        cursor.execute(
            "INSERT INTO usuario (nombre, email, contrasena, id_rol) VALUES (?,?,?,?)",
            ("Juan Empleado", "empleado@wamstock.com", hash_password("empleado123"), 2)
        )
        cursor.execute(
            "INSERT INTO usuario (nombre, email, contrasena, id_rol) VALUES (?,?,?,?)",
            ("Carlos Cliente", "carlos@correo.com", None, None)
        )
        cursor.execute("INSERT INTO cliente (cc_cliente, id_usuario) VALUES (?,?)", (1001, 3))

        cursor.execute(
            "INSERT INTO proveedor (nit_proveedor, nombre, contacto) VALUES (?,?,?)",
            (123, "Proveedor Central", "3001234567")
        )

        cursor.execute(
            "INSERT INTO producto (codigo_producto, nombre, precio, stock, nit_proveedor) VALUES (?,?,?,?,?)",
            (1, "Arroz", 2500, 20, 123)
        )
        cursor.execute(
            "INSERT INTO producto (codigo_producto, nombre, precio, stock, nit_proveedor) VALUES (?,?,?,?,?)",
            (2, "Aceite", 8500, 15, 123)
        )
        cursor.execute(
            "INSERT INTO producto (codigo_producto, nombre, precio, stock, nit_proveedor) VALUES (?,?,?,?,?)",
            (3, "Sal", 1500, 30, 123)
        )

        # Factura de prueba con detalle
        cursor.execute("INSERT INTO factura (cc_cliente, total) VALUES (?,?)", (1001, 13500))
        cursor.execute(
            "INSERT INTO factura_detalle (id_factura, id_producto, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
            (1, 1, 2, 2500, 5000)
        )
        cursor.execute(
            "INSERT INTO factura_detalle (id_factura, id_producto, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
            (1, 2, 1, 8500, 8500)
        )

        conn.commit()
        print("\n✅ Base de datos lista")
        print("   Tendero  → email: tendero@wamstock.com  | pass: tendero123")
        print("   Empleado → email: empleado@wamstock.com | pass: empleado123")

    except sqlite3.Error as e:
        print("Error:", e)
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    setup_database()