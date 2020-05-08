#1) CREAMOS EL ENTORNO VIRTUAL
Para ello realizamos
>>>python3 -m venv nombreentorno 
#2) INSTALAR LIBRERIAS NECESARIAS CON PIP
Activamos el entorno con source bin/activate
Hacemos:
>>>pip install -r requirements.txt
Donde el archivo txt contiene los nombres de las librerias usadas en el proyecto
#3) CREAR UN ESQUEMA DE BD MYSQL Y CONFIGURAR LOS PARAMETROS NECESARIOS EN create_engine en run_DB.py o utilizar un archivo .env para configurar dichos parametros. Esto ultimo se hizo en el proyecto.
#4) Ejecutar run_DB.py con el entorno activado. Esto creara la tabla tickets
#5) Usar el proyecto lanzando el servidor y el o los clientes

#NOTA: COLOCAR IP DE SERVIDOR EN run_DB en la ruta del connect cuando se usa otra pc que no sea localhost
