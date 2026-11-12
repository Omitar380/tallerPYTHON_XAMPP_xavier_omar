# Documentación del sistema CRUD de estudiantes

## Descripción

Esta aplicación web permite administrar los estudiantes de una institución educativa. Está desarrollada con Python y Flask, y guarda la información en MySQL, administrado localmente mediante XAMPP.

## Arquitectura

- **`app.py`** contiene la aplicación Flask, las rutas y la lógica que consulta o modifica la base de datos.
- **`templates/`** contiene las páginas HTML que Flask muestra en el navegador: listado, registro, edición y consulta individual.
- **`static/estilos.css`** define la presentación visual de las páginas.
- **MySQL** almacena los registros en la base de datos `institucion`, dentro de la tabla `estudiantes`.

La tabla almacena un identificador interno (`id`), número de identificación, nombre, apellido, correo electrónico y programa académico. El `id` es la clave primaria que permite identificar cada registro; la identificación del estudiante y el correo deben ser únicos.

## Funcionamiento

El usuario accede a la aplicación desde el navegador. Flask recibe cada solicitud, realiza la operación necesaria en MySQL mediante `mysql-connector-python` y devuelve la página HTML correspondiente.

- **Registrar:** la ruta `/crear` muestra el formulario y guarda un estudiante mediante una consulta `INSERT`.
- **Consultar listado y buscar:** la ruta `/` muestra los registros con `SELECT`. También permite filtrar por nombre o apellido.
- **Consultar un estudiante:** la ruta `/estudiante/<id>` presenta el detalle de un registro seleccionado.
- **Actualizar:** la ruta `/editar/<id>` permite modificar sus datos mediante `UPDATE`.
- **Eliminar:** la ruta `/eliminar/<id>` borra un registro mediante `DELETE` cuando se confirma la acción.

Las consultas SQL usan parámetros para enviar los valores a MySQL. Antes de guardar o actualizar, la aplicación comprueba que no se repitan la identificación ni el correo. También muestra mensajes de confirmación o error al usuario.

## Ejecución

Con MySQL iniciado desde XAMPP, se activa el entorno virtual y se ejecuta `python app.py` desde la carpeta del proyecto. Después se abre `http://127.0.0.1:5000` en el navegador.

La base debe tener la estructura definida en el proyecto. Si ya existían registros antes de agregar el campo de identificación, se debe ejecutar una sola vez `migracion.sql` desde phpMyAdmin para actualizar la tabla y asignar identificaciones temporales a esos registros.
