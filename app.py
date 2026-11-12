import os
import secrets

from flask import Flask, abort, flash, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector.errors import IntegrityError

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)


def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="institucion"
    )


def leer_datos_formulario():
    return {
        'identificacion': request.form.get('identificacion', '').strip(),
        'nombre': request.form.get('nombre', '').strip(),
        'apellido': request.form.get('apellido', '').strip(),
        'correo': request.form.get('correo', '').strip(),
        'programa': request.form.get('programa', '').strip(),
    }


def correo_ya_registrado(cursor, correo, excluir_id=None):
    if excluir_id is None:
        cursor.execute(
            "SELECT id FROM estudiantes WHERE LOWER(correo)=LOWER(%s)",
            (correo,)
        )
    else:
        cursor.execute(
            "SELECT id FROM estudiantes WHERE LOWER(correo)=LOWER(%s) AND id<>%s",
            (correo, excluir_id)
        )
    return cursor.fetchone() is not None


def identificacion_ya_registrada(cursor, identificacion, excluir_id=None):
    if excluir_id is None:
        cursor.execute(
            "SELECT id FROM estudiantes WHERE identificacion=%s",
            (identificacion,)
        )
    else:
        cursor.execute(
            "SELECT id FROM estudiantes WHERE identificacion=%s AND id<>%s",
            (identificacion, excluir_id)
        )
    return cursor.fetchone() is not None


@app.route('/crear', methods=['GET', 'POST'])
def crear():
    datos = {campo: '' for campo in ('identificacion', 'nombre', 'apellido', 'correo', 'programa')}
    if request.method == 'POST':
        datos = leer_datos_formulario()
        if not all(datos.values()):
            flash('Completa todos los campos.', 'error')
            return render_template('crear.html', datos=datos), 400

        conexion = conectar()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            if identificacion_ya_registrada(cursor, datos['identificacion']):
                flash('Ya existe un estudiante con ese número de identificación.', 'error')
                return render_template('crear.html', datos=datos), 409
            if correo_ya_registrado(cursor, datos['correo']):
                flash('Ese correo electrónico ya está registrado.', 'error')
                return render_template('crear.html', datos=datos), 409

            sql = """INSERT INTO estudiantes
                (identificacion, nombre, apellido, correo, programa)
                VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, tuple(datos[campo] for campo in
                                       ('identificacion', 'nombre', 'apellido', 'correo', 'programa')))
            conexion.commit()
        except IntegrityError:
            conexion.rollback()
            flash('No se pudo registrar: la identificación o el correo ya están en uso.', 'error')
            return render_template('crear.html', datos=datos), 409
        finally:
            if cursor is not None:
                cursor.close()
            conexion.close()

        flash('Estudiante registrado correctamente.', 'success')
        return redirect(url_for('index'))

    return render_template('crear.html', datos=datos)


@app.route('/')
def index():
    busqueda = request.args.get('busqueda', '').strip()
    conexion = conectar()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        if busqueda:
            termino = f"%{busqueda}%"
            cursor.execute(
                """SELECT * FROM estudiantes
                   WHERE nombre LIKE %s OR apellido LIKE %s
                   ORDER BY apellido, nombre""",
                (termino, termino)
            )
        else:
            cursor.execute("SELECT * FROM estudiantes ORDER BY apellido, nombre")
        estudiantes = cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()

    return render_template(
        'index.html',
        estudiantes=estudiantes,
        busqueda=busqueda
    )


@app.route('/estudiante/<int:id>')
def consultar_estudiante(id):
    conexion = conectar()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estudiantes WHERE id=%s", (id,))
        estudiante = cursor.fetchone()
        if estudiante is None:
            abort(404)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()

    return render_template('detalle.html', estudiante=estudiante)


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conexion = conectar()
    cursor = None
    datos = None
    try:
        cursor = conexion.cursor(dictionary=True)

        if request.method == 'POST':
            datos = leer_datos_formulario()
            if not all(datos.values()):
                flash('Completa todos los campos.', 'error')
                cursor.execute("SELECT * FROM estudiantes WHERE id=%s", (id,))
                estudiante = cursor.fetchone()
                if estudiante is None:
                    abort(404)
                estudiante.update(datos)
                return render_template('editar.html', estudiante=estudiante), 400

            cursor.execute("SELECT id FROM estudiantes WHERE id=%s", (id,))
            if cursor.fetchone() is None:
                abort(404)

            if identificacion_ya_registrada(cursor, datos['identificacion'], id):
                flash('Ya existe otro estudiante con ese número de identificación.', 'error')
            elif correo_ya_registrado(cursor, datos['correo'], id):
                flash('Ese correo electrónico ya está registrado por otro estudiante.', 'error')
            else:
                sql = """UPDATE estudiantes
                    SET identificacion=%s, nombre=%s, apellido=%s, correo=%s, programa=%s
                    WHERE id=%s"""
                cursor.execute(
                    sql,
                    tuple(datos[campo] for campo in
                          ('identificacion', 'nombre', 'apellido', 'correo', 'programa')) + (id,)
                )
                conexion.commit()
                flash('Datos del estudiante actualizados correctamente.', 'success')
                return redirect(url_for('index'))

            estudiante = {'id': id, **datos}
            return render_template('editar.html', estudiante=estudiante), 409

        cursor.execute("SELECT * FROM estudiantes WHERE id=%s", (id,))
        estudiante = cursor.fetchone()
        if estudiante is None:
            abort(404)
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()

    return render_template('editar.html', estudiante=estudiante)


@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conexion = conectar()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM estudiantes WHERE id=%s", (id,))
        eliminado = cursor.rowcount > 0
        conexion.commit()
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()

    if eliminado:
        flash('Estudiante eliminado correctamente.', 'success')
    else:
        flash('No se encontró el estudiante que intentabas eliminar.', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)