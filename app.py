

import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import wraps

import mysql.connector
from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, session, url_for
from flask_wtf import CSRFProtect, FlaskForm
from flask_wtf.csrf import CSRFError
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "cambiar-esta-clave-en-produccion")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["WTF_CSRF_TIME_LIMIT"] = None
csrf = CSRFProtect(app)


def _valor(*nombres, defecto=""):
    for nombre in nombres:
        if os.getenv(nombre):
            return os.getenv(nombre)
    return defecto


DB_CONFIG = {
    "host": _valor("MYSQL_HOST", "MYSQL_ADDON_HOST", defecto="localhost"),
    "user": _valor("MYSQL_USER", "MYSQL_ADDON_USER", defecto="root"),
    "password": _valor("MYSQL_PASSWORD", "MYSQL_ADDON_PASSWORD", defecto="bauti2502"),
    "database": _valor("MYSQL_DATABASE", "MYSQL_ADDON_DB", defecto="portfolio_db"),
    "port": int(_valor("MYSQL_PORT", "MYSQL_ADDON_PORT", defecto="3306")),
    "charset": "utf8mb4",
}


def conectar():
    return mysql.connector.connect(**DB_CONFIG)


def consultar(sql, params=()):
    conexion = conectar()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conexion.close()


def consultar_uno(sql, params=()):
    conexion = conectar()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    finally:
        conexion.close()


def ejecutar(sql, params=()):
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, params)
        conexion.commit()
    finally:
        conexion.close()


CLAVES = {
    "estudios": ("titulo", "institucion", "periodo", "descripcion"),
    "experiencias": ("puesto", "empresa", "periodo", "descripcion"),
    "tecnologias": ("nombre", "nivel", "icono"),
    "proyectos": ("titulo", "descripcion", "tecnologias", "url", "imagen"),
}

HASH_ADMIN = "scrypt:32768:8:1$nabWjcwCth3YPCVC$ddd963ab43a89f5f6a204f10815d5a188a52ec081e0cc31dd637fc53742e71edaadff37ac03ca5614d86516dc0b78dcbe18157af022c9fc03de82a11d6762337"


def asegurar_base():
    conexion = None
    try:
        conexion = conectar()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            base = cursor.fetchone()[0]
            for tabla in CLAVES:
                cursor.execute(
                    """SELECT COUNT(*) FROM information_schema.COLUMNS
                       WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = 'orden'""",
                    (base, tabla),
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        f"ALTER TABLE {tabla} ADD COLUMN orden INT NOT NULL DEFAULT 0"
                    )
            cursor.execute(
                "INSERT IGNORE INTO usuarios (id, username, password_hash) VALUES (1, %s, %s)",
                ("admin", HASH_ADMIN),
            )
            cursor.execute(
                """INSERT IGNORE INTO perfil (id, nombre, titulo, descripcion)
                   VALUES (1, %s, %s, %s)""",
                (
                    PERFIL_INICIAL["nombre"],
                    PERFIL_INICIAL["titulo"],
                    PERFIL_INICIAL["descripcion"],
                ),
            )
        conexion.commit()
    except mysql.connector.Error as error:
        app.logger.warning("No se pudo preparar la base de datos: %s", error.msg)
    finally:
        if conexion:
            conexion.close()


# POO - PILAR 1: ABSTRACCIÓN.
# "Seccion" define la interfaz común (listar, etiqueta, describir) y oculta
# los detalles de MySQL: las plantillas sólo reciben listas de datos.
class Seccion(ABC):
    @abstractmethod
    def listar(self):
        """Cada sección concreta entrega sus registros."""

    @abstractmethod
    def etiqueta(self):
        """Nombre legible usado en el panel de edición."""

    def describir(self):
        return f"{len(self.listar())} {self.etiqueta()}"


# POO - PILAR 2: ENCAPSULAMIENTO.
# Los atributos __tabla y __claves son privados: se leen con propiedades y
# nadie puede modificar la estructura de la sección desde fuera de la clase.
class Coleccion(Seccion):
    def __init__(self, tabla, claves):
        self.__tabla = tabla
        self.__claves = claves

    @property
    def tabla(self):
        return self.__tabla

    @property
    def claves(self):
        return self.__claves

    def listar(self):
        columnas = ", ".join(("id",) + self.__claves)
        return consultar(f"SELECT {columnas} FROM {self.__tabla} ORDER BY orden, id")

    def guardar(self, filas):
        conexion = conectar()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.__tabla}")
                columnas = ", ".join(self.__claves + ("orden",))
                marcadores = ", ".join(["%s"] * (len(self.__claves) + 1))
                sql = f"INSERT INTO {self.__tabla} ({columnas}) VALUES ({marcadores})"
                for orden, fila in enumerate(filas, 1):
                    cursor.execute(sql, fila + (orden,))
            conexion.commit()
        finally:
            conexion.close()


# POO - PILAR 3: HERENCIA.
# Estudios, Experiencias, Tecnologías y Proyectos reutilizan Coleccion;
# cada subclass heredada recibe su tabla y sus columnas.
class Estudios(Coleccion):
    def __init__(self):
        super().__init__("estudios", CLAVES["estudios"])

    def etiqueta(self):
        return "estudios"


class Experiencias(Coleccion):
    def __init__(self):
        super().__init__("experiencias", CLAVES["experiencias"])

    def etiqueta(self):
        return "experiencias"


class Tecnologias(Coleccion):
    def __init__(self):
        super().__init__("tecnologias", CLAVES["tecnologias"])

    def etiqueta(self):
        return "tecnologías"


class Proyectos(Coleccion):
    def __init__(self):
        super().__init__("proyectos", CLAVES["proyectos"])

    def etiqueta(self):
        return "proyectos"


# POO - PILAR 4: POLIMORFISMO.
# El mismo mensaje describir() produce resultados distintos: cada objeto
# usa su propia etiqueta sin que el llamador tenga que preguntar su tipo.
secciones = (Estudios(), Experiencias(), Tecnologias(), Proyectos())


class Usuario:
    def __init__(self, fila, rol="visitante"):
        self.id = fila["id"]
        self.username = fila["username"]
        self.rol = rol
        self.__hash = fila["password_hash"]

    def verificar(self, password):
        return check_password_hash(self.__hash, password)


class Admin(Usuario):
    def __init__(self, fila):
        super().__init__(fila, "admin")

    def puede_editar(self):
        return self.rol == "admin"


class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(), Length(max=50)])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    remember = BooleanField("Recordarme")
    submit = SubmitField("Ingresar")


PERFIL_INICIAL = {
    "nombre": "Tu nombre y apellido",
    "titulo": "Desarrollador Full Stack",
    "descripcion": "Contanos brevemente quién sos y qué te motiva.",
    "email": "tu@email.com",
    "telefono": "+54 9 11 0000-0000",
    "ubicacion": "Buenos Aires, Argentina",
    "github": "https://github.com/tu-usuario",
    "linkedin": "https://www.linkedin.com/in/tu-usuario",
    "cv": "CV.pdf",
}

asegurar_base()


def parsear(texto, claves):
    filas = []
    for linea in texto.splitlines():
        partes = [parte.strip() for parte in linea.split("|")]
        if not any(partes):
            continue
        partes += [""] * (len(claves) - len(partes))
        filas.append(tuple(partes[: len(claves)]))
    return filas


def a_texto(filas, claves):
    return "\n".join(
        " | ".join(str(fila.get(clave, "")) for clave in claves) for fila in filas
    )


def cargar_datos():
    perfil = PERFIL_INICIAL | (consultar_uno("SELECT * FROM perfil WHERE id = 1") or {})
    listados = {seccion.tabla: seccion.listar() for seccion in secciones}
    textos = {
        tabla: a_texto(filas, CLAVES[tabla]) for tabla, filas in listados.items()
    }
    resumen = [
        f"{len(listados[seccion.tabla])} {seccion.etiqueta()}" for seccion in secciones
    ]
    return perfil, textos, resumen


@app.context_processor
def datos_comunes():
    return {"anio": datetime.now().year}


@app.errorhandler(CSRFError)
def csrf_error(error):
    flash("La sesión venció o el formulario cambió. Recargá la página e intentá de nuevo.", "error")
    return redirect(request.referrer or url_for("admin"))


def login_required(vista):
    @wraps(vista)
    def envolver(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return vista(*args, **kwargs)

    return envolver


@app.route("/")
def index():
    perfil = PERFIL_INICIAL | (consultar_uno("SELECT * FROM perfil WHERE id = 1") or {})
    contenido = {seccion.tabla: seccion.listar() for seccion in secciones}
    return render_template(
        "index.html", perfil=perfil, anio=datetime.now().year, **contenido
    )


@app.route("/descargar-cv")
def descargar_cv():
    try:
        perfil = PERFIL_INICIAL | (consultar_uno("SELECT * FROM perfil WHERE id = 1") or {})
    except mysql.connector.Error:
        perfil = PERFIL_INICIAL
    nombre = os.path.basename(perfil.get("cv") or "CV.pdf")
    ruta = os.path.join(app.static_folder, nombre)
    if not os.path.isfile(ruta):
        abort(404)
    return send_from_directory(app.static_folder, nombre, as_attachment=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin"):
        return redirect(url_for("admin"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            fila = consultar_uno("SELECT * FROM usuarios WHERE username = %s", (form.username.data,))
        except mysql.connector.Error as error:
            flash(f"No se pudo conectar con la base de datos: {error.msg}", "error")
            return render_template("login.html", form=form)
        usuario = Admin(fila) if fila else None
        if usuario and usuario.verificar(form.password.data) and usuario.puede_editar():
            session.clear()
            session["admin"] = usuario.username
            session.permanent = form.remember.data
            flash("Sesión iniciada. Ya podés editar el portfolio.", "ok")
            return redirect(url_for("admin"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    flash("Cerraste sesión.", "ok")
    return redirect(url_for("index"))


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if request.method == "POST":
        perfil = {clave: request.form.get(clave, "") for clave in PERFIL_INICIAL}
        textos = {
            seccion.tabla: request.form.get(seccion.tabla, "") for seccion in secciones
        }
        try:
            ejecutar(
                """UPDATE perfil SET nombre=%s, titulo=%s, descripcion=%s, email=%s,
                   telefono=%s, ubicacion=%s, github=%s, linkedin=%s, cv=%s WHERE id=1""",
                tuple(perfil[clave] for clave in PERFIL_INICIAL),
            )
            for seccion in secciones:
                seccion.guardar(parsear(textos[seccion.tabla], seccion.claves))
        except mysql.connector.Error as error:
            flash(f"No se pudo guardar: {error.msg}", "error")
            resumen = [
                f"{len(parsear(textos[seccion.tabla], seccion.claves))} {seccion.etiqueta()}"
                for seccion in secciones
            ]
            return render_template(
                "admin.html",
                perfil=perfil,
                textos=textos,
                resumen=resumen,
                claves=CLAVES,
            )
        flash("Portfolio actualizado correctamente.", "ok")
        return redirect(url_for("admin"))

    try:
        perfil, textos, resumen = cargar_datos()
    except mysql.connector.Error as error:
        flash(f"No se pudo cargar el panel: {error.msg}", "error")
        return redirect(url_for("index"))
    return render_template(
        "admin.html",
        perfil=perfil,
        textos=textos,
        resumen=resumen,
        claves=CLAVES,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=os.getenv("FLASK_DEBUG") == "1")
