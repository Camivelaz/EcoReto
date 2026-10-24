import sqlite3
from functools import wraps

from flask import (
    Blueprint, current_app, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash


rutas = Blueprint("rutas", __name__)


def conectar_db():
    conexion = sqlite3.connect(current_app.config["DATABASE"])
    conexion.row_factory = sqlite3.Row
    return conexion


def iniciar_sesion_requerido(funcion):
    @wraps(funcion)
    def comprobar(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("rutas.inicio"))
        return funcion(*args, **kwargs)
    return comprobar


@rutas.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")

        with conectar_db() as db:
            cuenta = db.execute(
                "SELECT * FROM usuarios WHERE usuario = ?",
                (usuario,)
            ).fetchone()

        if cuenta and check_password_hash(
            cuenta["contrasena"], contrasena
        ):
            session.clear()
            session["usuario_id"] = cuenta["id"]
            session["usuario"] = cuenta["usuario"]
            return redirect(url_for("rutas.inicio"))

        flash("Usuario o contraseña incorrectos.", "error")

    if "usuario_id" in session:
        with conectar_db() as db:
            acciones = db.execute("""
                SELECT * FROM acciones
                WHERE usuario_id = ?
                ORDER BY fecha DESC, id DESC
            """, (session["usuario_id"],)).fetchall()

        litros = sum(
            a["impacto"] for a in acciones
            if a["unidad"] == "litros"
        )
        kilos = sum(
            a["impacto"] for a in acciones
            if a["unidad"] == "kg"
        )
        kwh = sum(
            a["impacto"] for a in acciones
            if a["unidad"] == "kWh"
        )

        return render_template(
            "index.html",
            acciones=acciones,
            total=len(acciones),
            litros=litros,
            kilos=kilos,
            kwh=kwh
        )

    return render_template(
        "index.html",
        registro=request.args.get("registro") == "1"
    )


@rutas.route("/registro", methods=["POST"])
def registro():
    usuario = request.form.get("usuario", "").strip()
    contrasena = request.form.get("contrasena", "")

    if len(usuario) < 3 or len(contrasena) < 6:
        flash(
            "Usa un usuario de al menos 3 caracteres "
            "y una contraseña de al menos 6.",
            "error"
        )
        return redirect(url_for("rutas.inicio", registro=1))

    try:
        with conectar_db() as db:
            db.execute("""
                INSERT INTO usuarios (usuario, contrasena)
                VALUES (?, ?)
            """, (
                usuario,
                generate_password_hash(contrasena)
            ))
        flash("Cuenta creada. Ya puedes iniciar sesión.", "ok")
        return redirect(url_for("rutas.inicio"))

    except sqlite3.IntegrityError:
        flash("Ese usuario ya existe.", "error")
        return redirect(url_for("rutas.inicio", registro=1))


@rutas.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("rutas.inicio"))


@rutas.route("/nueva", methods=["GET", "POST"])
@iniciar_sesion_requerido
def nueva():
    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()
        unidad = request.form.get("unidad", "").strip()

        try:
            impacto = float(request.form.get("impacto", ""))
        except ValueError:
            impacto = -1

        tipos = [
            "Reciclaje", "Ahorro de agua",
            "Transporte", "Energía", "Otro"
        ]

        if (
            tipo not in tipos
            or not descripcion
            or len(descripcion) > 250
            or not fecha
            or unidad not in ["kg", "litros", "kWh", "unidades"]
            or impacto < 0
            or impacto > 1000000
        ):
            flash("Revisa los datos del formulario.", "error")
            return render_template(
                "formulario.html",
                accion=None,
                hoy=__import__("datetime").date.today().isoformat()
            )

        with conectar_db() as db:
            db.execute("""
                INSERT INTO acciones
                (usuario_id, tipo, descripcion, fecha, impacto, unidad)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session["usuario_id"], tipo, descripcion,
                fecha, impacto, unidad
            ))

        flash("¡Acción ecológica guardada!", "ok")
        return redirect(url_for("rutas.inicio"))

    from datetime import date
    return render_template(
        "formulario.html",
        accion=None,
        hoy=date.today().isoformat()
    )


@rutas.route("/editar/<int:id>", methods=["GET", "POST"])
@iniciar_sesion_requerido
def editar(id):
    with conectar_db() as db:
        accion = db.execute("""
            SELECT * FROM acciones
            WHERE id = ? AND usuario_id = ?
        """, (id, session["usuario_id"])).fetchone()

    if accion is None:
        flash("No se encontró esa acción.", "error")
        return redirect(url_for("rutas.inicio"))

    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()
        unidad = request.form.get("unidad", "").strip()

        try:
            impacto = float(request.form.get("impacto", ""))
        except ValueError:
            impacto = -1

        if (
            tipo not in [
                "Reciclaje", "Ahorro de agua",
                "Transporte", "Energía", "Otro"
            ]
            or not descripcion
            or len(descripcion) > 250
            or not fecha
            or unidad not in ["kg", "litros", "kWh", "unidades"]
            or impacto < 0
            or impacto > 1000000
        ):
            flash("Revisa los datos del formulario.", "error")
            return render_template(
                "formulario.html", accion=accion, hoy=accion["fecha"]
            )

        with conectar_db() as db:
            db.execute("""
                UPDATE acciones
                SET tipo = ?, descripcion = ?, fecha = ?,
                    impacto = ?, unidad = ?
                WHERE id = ? AND usuario_id = ?
            """, (
                tipo, descripcion, fecha, impacto, unidad,
                id, session["usuario_id"]
            ))

        flash("Acción actualizada correctamente.", "ok")
        return redirect(url_for("rutas.inicio"))

    return render_template(
        "formulario.html", accion=accion, hoy=accion["fecha"]
    )


@rutas.route("/eliminar/<int:id>", methods=["POST"])
@iniciar_sesion_requerido
def eliminar(id):
    with conectar_db() as db:
        db.execute("""
            DELETE FROM acciones
            WHERE id = ? AND usuario_id = ?
        """, (id, session["usuario_id"]))

    flash("Acción eliminada.", "ok")
    return redirect(url_for("rutas.inicio"))


@rutas.route("/detalle/<int:id>")
@iniciar_sesion_requerido
def detalle(id):
    with conectar_db() as db:
        accion = db.execute("""
            SELECT * FROM acciones
            WHERE id = ? AND usuario_id = ?
        """, (id, session["usuario_id"])).fetchone()

    if accion is None:
        flash("No se encontró esa acción.", "error")
        return redirect(url_for("rutas.inicio"))

    return render_template("detalle.html", accion=accion)