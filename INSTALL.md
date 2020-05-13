# Clonar repositorio
##### 1) Nos dirigimos al directorio donde se clonara el repositorio.

##### 2) Ejecutamos el git clone del repositorio:
```sh
git clone https://gitlab.com/SantiagoR98/sistema-de-tickets.git
```
# Pasos para la instalación
##### 1) CREAMOS EL ENTORNO VIRTUAL
Para ello nos paramos dentro del repositorio anteriormente clonado y hacemos
```sh
python3 -m venv .
```
##### 2) Entramos en el entorno virtual:
Ejecutamos lo siguiente dentro del directorio del repositorio:
```sh
source bin/activate
```

##### 3) Instalamos librerias necesarias para el proyecto con pip
Para ello hacemos:
```sh
pip install -r requirements.txt
```
##### 4) Poner en marcha nuestra Base de Datos:
Para ello debemos crear un esquema MySQL y a su vez crear un archivo **.env**
En el archivo **.env** setearemos lo siguiente:
```sh
export DB_USERNAME=nombre_usuario_bd
export DB_PASS=contraseña_bd
export DB_NAME=nombre_esquema_bd
```
Posteriormente procedemos a guardar el archivo.
##### 4) Ejecutar run_DB.py con el entorno activado. 
Esto creara la tabla tickets donde el servidor ira almacenando los tickets de los clientes.
##### 5) Finalmente ya estamos listos para proceder a ejecutar nuestro servidor y el o los clientes.
Para ello proseguir leyendo el archivo **README.md**
