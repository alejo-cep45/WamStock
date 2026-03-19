# WamStock
Gestión de inventario para pequeños negocios 

Para ejecutar el archivo primero vamos a crear el entorno virtual de python con: python -m venv .venv

Despues ejecutamos el entorno virtual con: .\.venv\Scripts\activate
Ejecutamos la base de datos que creeara el archivo inventario.db con el comando: python init_db.py

Ahora instalamos las dependencias necesarias: pip install -r '.\requirements.txt' 

Para ejecutar el programa ejecutamos lo siguiente: python '.\app.py'

En la linea de comandos nos dara un link al cual accederemos con ctrl+click

Luego en la barra del navegador al final agregamos "/productos" para ver los prodctos, y tambien podremos ver :
/clientes, /proveedores, /facturas, /empelados, /tendero, /usuarios.


Juan Alejandro Cepeda
