# Sistema de Tickets
Sistema de Tickets hecho en Python utilizando el ORM
[![N|Solid](https://www.sqlalchemy.org/img/sqla_logo.png)](https://www.sqlalchemy.org/)
Se implementaron Sockets siguiendo el Protocolo TCP para el diseño tanto del servidor como del cliente.
# Ayuda y uso básico de la aplicación
#### Servidor
Al momento de ejecutar el **servidor.py** se realiza de la siguiente manera:

  - ######  **python3 servidor.py -p nro_puerto**
    - Donde -p o --puerto es la opción **obligatoria** para definir el puerto en el que se atendera el servidor.

Luego de esto estamos listos para lanzar el cliente.

#### Cliente
En el caso del cliente, al ejecutar **cliente.py** se realiza de la siguiente manera:
  - ######  **python3 cliente.py -p nro_puerto -h ip_servidor**
    - Donde -p o --puerto es la opción **obligatoria** para definir el puerto al cual debe conectarse el socket cliente.
    - Donde -h o --host es la opción **obligatoria** para determinar cual es la IP del socket servidor al que deseamos conectarnos.

Una vez lanzado el cliente, dispondremos de los siguientes comandos:
### Comandos Disponibles
Los comandos estan presentados en  **opción larga/opción corta**:

	--insertar/-i : Procedemos a crear un ticket de soporte.
	--listar/-l : listamos tickets creados, o filtramos por autor, estado o fecha.
	--editar/-e nro_ticket : Procedemos a editar un ticket en particular.
	--exportar/-x : Exportamos un archivo CSV con la lista completa de tickets o filtrando por autor, estado o fecha.
	Utilizar:
			-a nombre_autor
			-d estado (estos son: pendiente, "en procesamiento" (escribir con comillas), resuelto)
			-f fecha (DD-MM-YYYY)
	--clear/-c : limpia la pantalla de la consola.
	--salir/-s : sale del programa.

