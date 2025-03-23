from flask import render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from db import app, mysql  

load_dotenv()

@app.route("/eliminarUsuario", methods=["POST"])
def eliminarUsuario():
    idUsuario = request.form["idUsuario"]
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE usuarios SET status = 0 WHERE idUsuario = %s;",
        (idUsuario,)
    )
    mysql.connection.commit()
    cur.close()

    flash("✅ Usuario eliminado con éxito", "success")
    return redirect(url_for("usuarios"))


@app.route("/activarUsuario", methods=["POST", "GET"])
def activarUsuario():
    if request.method == "POST":
        idUsuario = request.form["idUsuario"]
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE usuarios SET status = 1 WHERE idUsuario = %s;",
            (idUsuario,),
        )
        mysql.connection.commit()
        cur.close()
        flash("Usuario activado con éxito", "success")
        return redirect(url_for("usuarios"))
    usuarios = get_users()
    return render_template("/usuario/usuarios.html", usuarios=usuarios)


@app.route("/eliminarDefUsuario", methods=["POST"])
def deleteUsuario():
    idUsuario = request.form["idUsuario"]
    cur = mysql.connection.cursor()
    cur.execute(
        "DELETE FROM usuarios WHERE idUsuario = %s;",
        (idUsuario,),
    )
    mysql.connection.commit()
    cur.close()
    flash("Usuario eliminado permanentemente", "success")
    return redirect(url_for("usuarios"))


@app.route("/usuarios", methods=["GET"])
def usuarios():
    user = session.get("user")
    usuarios = get_users()
    return render_template("/usuario/Usuario.html", usuarios=usuarios, user=user)


@app.route("/registerUsuario", methods=["POST"])
def registerUsuario():
    nombreEmpleado = request.form["nombreEmpleado"]
    puesto = request.form["puesto"]
    apellidoP = request.form["apellidoP"]
    apellidoM = request.form["apellidoM"]
    telefono = request.form["tel"]
    email = request.form["email"]
    contrasenia = generate_password_hash(request.form["contrasenia"])
    rol = request.form["rol"]
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO empleado (nombreEmpleado, puesto, apellidoP, apellidoM, telefono) VALUES (%s, %s, %s, %s, %s);",
        (nombreEmpleado, puesto, apellidoP, apellidoM,telefono)
    )
    idEmpleado = cur.lastrowid
    cur.execute(
        "INSERT INTO usuarios (email, password, rol, idEmpleadoFK) VALUES (%s, %s, %s, %s)",
        (email,contrasenia,rol, idEmpleado),
    )
    mysql.connection.commit()
    cur.close()
    
    flash("Usuario registrado con éxito", "success")
    return redirect(url_for("usuarios"))

@app.route("/modifyUsuario", methods=["POST", "GET"])
def modifyUsuario():
    if request.method == "POST":
        idEmpleado = request.form.get("idEmpleado")
        idUsuario = request.form.get("idUsuario")
        nombreEmpleado = request.form.get("nombreEmpleado")
        apellidoP = request.form.get("apellidoP")
        apellidoM = request.form.get("apellidoM")
        puesto = request.form.get("puesto")
        telefono = request.form.get("telefono")
        idUsuario = request.form.get("idUsuario") 
        email = request.form["email"]
        rol = request.form["rol"]
        password = request.form["contrasenia"]
        if idUsuario:
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE empleado SET nombreEmpleado = %s, apellidoP = %s, apellidoM = %s, puesto = %s, telefono = %s WHERE idEmpleado=%s",
                (nombreEmpleado, apellidoP, apellidoM, puesto, telefono, idEmpleado)
            )
            cur.execute(
                "UPDATE usuarios SET password=%s, email=%s, rol=%s WHERE idUsuario=%s",
                (email, rol,password, idUsuario),
            )
            mysql.connection.commit()
            cur.close()
            flash("Usuario actualizado con éxito", "success")
        return redirect(url_for("usuarios_dashboard"))
    usuarios = get_users()
    return render_template("/usuario/Usuario.html", usuarios=usuarios)


def get_users(estado=1):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT idUsuario, email,e.puesto,password, rol, CONCAT(e.nombreEmpleado, ' ', e.apellidoP,' ',e.apellidoM) as nombreEmpleado,e.telefono
        FROM usuarios u
        LEFT JOIN empleado e ON u.idEmpleadoFK = e.idEmpleado
        WHERE u.status = %s;
    """, (estado,))
    columnas = [col[0] for col in cur.description]
    usuarios = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
    cur.close()
    return usuarios


@app.route("/getUsuarios", methods=["GET"])
def get_users_json():
    estado = request.args.get("estado", default=1, type=int)
    usuarios = get_users(estado)
    return {"usuarios": usuarios}