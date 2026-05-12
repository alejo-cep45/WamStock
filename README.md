# WamStock 🛒
> Sistema de gestión de inventario para pequeños negocios con persistencia políglota, autenticación JWT y control de acceso por roles.

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3 + Flask |
| Base de datos relacional | SQLite |
| Base de datos no relacional | MongoDB Atlas |
| Autenticación | JWT (Flask-JWT-Extended) |
| Encriptación | bcrypt |
| Frontend | Jinja2 + HTML + CSS + JavaScript |

---

## Arquitectura

El proyecto implementa **persistencia políglota**: usa dos motores de base de datos con responsabilidades distintas.

- **SQLite** — fuente de verdad: usuarios, roles, productos, clientes, proveedores, facturas y su detalle.
- **MongoDB** — historial y auditoría: logs de movimientos, sesiones, alertas de stock bajo y snapshots de ventas con precios históricos.

La API sigue una estructura de **Blueprints** de Flask, separando cada módulo en su propio archivo:

```
wamstock/
├── app.py                  ← inicialización y rutas HTML
├── config.py               ← configuración centralizada
├── database.py             ← conexiones SQLite y MongoDB
├── init_db.py              ← creación e inicialización de la BD
├── requirements.txt
│
├── auth/
│   ├── decorators.py       ← @tendero, @empleado
│   └── routes.py           ← /auth/login, /auth/me
│
├── routes/
│   ├── clientes.py
│   ├── facturas.py
│   ├── logs.py
│   ├── productos.py
│   ├── proveedores.py
│   ├── roles.py
│   └── usuarios.py
│
├── templates/              ← páginas HTML (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── ventas.html
│   ├── facturas.html
│   ├── productos.html
│   ├── clientes.html
│   ├── proveedores.html
│   ├── usuarios.html
│   └── logs.html
│
└── static/
    └── style.css
```

---

## Roles y permisos (RBAC)

El sistema implementa dos niveles de acceso. El tendero hereda todos los permisos del empleado.

| Acción | Empleado | Tendero |
|---|:---:|:---:|
| Ver productos, facturas, clientes, proveedores | ✅ | ✅ |
| Crear y editar productos | ✅ | ✅ |
| Registrar ventas y facturas | ✅ | ✅ |
| Eliminar productos | ❌ | ✅ |
| Gestionar clientes y proveedores | ❌ | ✅ |
| Gestionar usuarios y roles | ❌ | ✅ |
| Ver logs de sesiones | ❌ | ✅ |

Los decoradores se aplican directamente sobre cada endpoint:

```python
@app.route('/api/productos', methods=['DELETE'])
@jwt_required()
@tendero          # solo tendero puede eliminar
def delete_producto():
    ...
```

---

## Instalación y ejecución

### 1. Clonar el repositorio y entrar a la carpeta

```bash
git clone <url-del-repo>
cd wamstock
```

### 2. Crear y activar el entorno virtual

```bash
# Crear
python -m venv .venv

# Activar en Windows
.\.venv\Scripts\activate

# Activar en Mac/Linux
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Inicializar la base de datos

```bash
python init_db.py
```

Esto crea el archivo `inventario.db` con las tablas y datos de prueba.

### 5. Ejecutar la aplicación

```bash
python app.py
```

La app queda disponible en `http://127.0.0.1:5000`

---

## Credenciales de prueba

| Rol | Email | Contraseña |
|---|---|---|
| Tendero (admin) | tendero@wamstock.com | tendero123 |
| Empleado | empleado@wamstock.com | empleado123 |

---

## Endpoints API

Todas las rutas de la API requieren el header:
```
Authorization: Bearer <token>
```

El token se obtiene desde `POST /auth/login`.

| Método | Ruta | Descripción | Rol mínimo |
|---|---|---|---|
| POST | `/auth/login` | Iniciar sesión | — |
| GET | `/auth/me` | Info del usuario autenticado | empleado |
| GET | `/api/productos` | Listar productos | empleado |
| POST | `/api/productos` | Crear producto | empleado |
| PUT | `/api/productos/<id>` | Editar producto | empleado |
| DELETE | `/api/productos/<id>` | Eliminar producto | tendero |
| GET | `/api/facturas` | Listar facturas con detalle | empleado |
| POST | `/api/facturas` | Crear factura (múltiples items) | empleado |
| DELETE | `/api/facturas/<id>` | Eliminar factura y restaurar stock | tendero |
| GET | `/api/clientes` | Listar clientes | empleado |
| POST | `/api/clientes` | Crear cliente | tendero |
| GET | `/api/proveedores` | Listar proveedores | empleado |
| POST | `/api/proveedores` | Crear proveedor | tendero |
| GET | `/api/usuarios` | Listar usuarios | tendero |
| POST | `/api/usuarios` | Crear usuario | tendero |
| GET | `/api/roles` | Listar roles | tendero |
| GET | `/api/logs` | Logs de movimientos (MongoDB) | empleado |
| GET | `/api/logs/sesiones` | Historial de logins (MongoDB) | tendero |
| GET | `/api/logs/alertas-stock` | Alertas de stock bajo (MongoDB) | empleado |
| GET | `/api/logs/facturas-detalle` | Snapshots históricos de ventas (MongoDB) | empleado |

---

## Colecciones MongoDB

Se implementó un sistema de registro de eventos utilizando MongoDB, lo que permite almacenar el historial de acciones del sistema sin afectar el rendimiento de la base de datos principal.

| Colección | Cuándo se escribe |
|---|---|
| `movimientos_log` | Al actualizar un producto o registrar una venta |
| `sesiones_log` | En cada login exitoso (guarda IP, rol y fecha) |
| `alertas_stock` | Cuando el stock de un producto queda en ≤ 5 unidades |
| `facturas_detalle` | Al crear una factura (snapshot con precios al momento de la venta) |

### Ejemplo — historial de un producto

`GET /api/productos/1/historial`

```json
{
  "producto": { "codigo_producto": 1, "nombre": "Arroz", "precio": 2500, "stock": 18 },
  "historial": [
    {
      "tipo": "actualizacion_producto",
      "producto": 1,
      "datos": { "stock": 18 },
      "modificado_por": "Admin Tendero",
      "rol": "tendero",
      "fecha": "2026-05-10T00:51:00"
    }
  ]
}
```

### Ejemplo — logs generales

`GET /api/logs`

```json
[
  {
    "tipo": "venta",
    "id_factura": 3,
    "cliente": 1001,
    "total": 13500,
    "registrado_por": "Juan Empleado",
    "rol": "empleado",
    "fecha": "2026-05-10T00:51:00"
  }
]
```
<img width="1919" height="915" alt="image" src="https://github.com/user-attachments/assets/955b3689-0889-4dd6-9293-df5bde8073a7" />



---

## Autor

Juan Alejandro Cepeda
