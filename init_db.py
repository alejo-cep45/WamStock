import sqlite3

def setup_database():
    try:
        conn = sqlite3.connect('inventario.db')
        cursor = conn.cursor()

        print("Creando tablas...")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE
            )
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cliente (
                cc_cliente INTEGER PRIMARY KEY,
                id_usuario INTEGER,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            )
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empleado (
                id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                contrasena TEXT NOT NULL,
                id_usuario INTEGER,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            )
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tendero (
                id_tendero INTEGER PRIMARY KEY AUTOINCREMENT,
                contrasena TEXT NOT NULL,
                id_usuario INTEGER,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            )
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedor (
                nit_proveedor INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                contacto TEXT
            )
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS producto (
                codigo_producto INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                precio REAL,
                stock INTEGER DEFAULT 0,
                nit_proveedor INTEGER,
                FOREIGN KEY (nit_proveedor) REFERENCES proveedor(nit_proveedor)
            )
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS factura (
                id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
                cc_cliente INTEGER,
                id_producto INTEGER,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cc_cliente) REFERENCES cliente(cc_cliente),
                FOREIGN KEY (id_producto) REFERENCES producto(codigo_producto)
            )
        ''')

        print("Insertando datos de prueba...")

        cursor.execute("INSERT INTO usuario (nombre, email) VALUES (?, ?)",
                       ("Admin", "admin@test.com"))

        cursor.execute("INSERT INTO cliente (cc_cliente, id_usuario) VALUES (?, ?)",
                       (1001, 1))

        cursor.execute("INSERT INTO empleado (contrasena, id_usuario) VALUES (?, ?)",
                       ("1234", 1))

        cursor.execute("INSERT INTO tendero (contrasena, id_usuario) VALUES (?, ?)",
                       ("abcd", 1))

        cursor.execute("INSERT INTO proveedor (nit_proveedor, nombre, contacto) VALUES (?, ?, ?)",
                       (123, "Proveedor Central", "3001234567"))

        cursor.execute("INSERT INTO producto (codigo_producto, nombre, precio, stock, nit_proveedor) VALUES (?, ?, ?, ?, ?)",
                       (1, "Arroz", 2500, 20, 123))

        cursor.execute("INSERT INTO factura (cc_cliente, id_producto) VALUES (?, ?)",
                       (1001, 1))

        conn.commit()
        print("Base de datos lista")

    except sqlite3.Error as e:
        print("Error:", e)

    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    setup_database()