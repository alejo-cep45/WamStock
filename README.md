# WamStock
Gestión de inventario para pequeños negocios 

Para ejecutar el archivo primero vamos a crear el entorno virtual de python con: `python -m venv .venv`

Despues ejecutamos el entorno virtual con: `.\.venv\Scripts\activate`
Ejecutamos la base de datos que creeara el archivo inventario.db con el comando: `python init_db.py`

Ahora instalamos las dependencias necesarias: `pip install -r '.\requirements.txt' `

Para ejecutar el programa ejecutamos lo siguiente: `python '.\app.py'`

En la linea de comandos nos dara un link al cual accederemos con ctrl+click

Luego en la barra del navegador al final agregamos "/productos" para ver los prodctos, y tambien podremos ver :
/clientes, /proveedores, /facturas, /empelados, /tendero, /usuarios.

<img width="1919" height="632" alt="image" src="https://github.com/user-attachments/assets/779efd6c-01db-47b4-abb2-e7a9a2e148d9" />

Se implemento un sistema de registro de eventos (logs) utilizando MongoDB, lo que permite almacenar el historial de acciones del sistema sin afectar el rendimiento de la base de datos principal.



El proyecto utiliza dos tipos de bases de datos:

## (SQLite)

Se encarga de almacenar la información estructurada del sistema:

- Usuarios
- Productos
- Facturas
- Relaciones entre entidades

## Base de Datos NoSQL (MongoDB Atlas)

Se utiliza para almacenar eventos y registros de actividad del sistema:

- Ventas realizadas
- Actualizaciones de productos
- Acciones relevantes del sistema


Por ejemplo este endpoint `http://127.0.0.1:5000/productos/1/historial`
Da como resultado esta respuesta

<img width="921" height="689" alt="image" src="https://github.com/user-attachments/assets/c04b019a-e686-4aca-86ed-c354eb8ac300" />


`http://127.0.0.1:5000/logs`
<img width="572" height="435" alt="image" src="https://github.com/user-attachments/assets/0acd27af-c19a-47ec-a587-1468072bbd9a" />


Juan Alejandro Cepeda
