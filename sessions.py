from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from db import app, mysql, captcha

#! ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////// Logica de sesiones de la app ///////////////////////////////////////////////////////////////////////
#! ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@app.route("/login", methods=["GET", "POST"])
def login():
    new_captcha_dict = captcha.create()
    user = session.get("user")
    if user is not None:
        match user[4]:
            case "administrador":
                return redirect(url_for("admin_dashboard"))
            case "produccion":
                return redirect(url_for("produccion_dashboard"))
            case "ventas":
                return redirect(url_for("ventas_dashboard"))
            case "cliente":
                return redirect(url_for("cliente_dashboard"))
    else:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios where email = %s", (email,))
            userDb = cur.fetchone()
            cur.close()
            if userDb and check_password_hash(userDb[3], password):
                session["user"] = userDb
                role = userDb[4]
                match role:
                    case "administrador":
                        return redirect(url_for("admin_dashboard"))
                    case "produccion":
                        return redirect(url_for("produccion_dashboard"))
                    case "ventas":
                        return redirect(url_for("ventas_dashboard"))
                    case "cliente":
                        return redirect(url_for("cliente_dashboard"))
            else:
                flash("Usuario o contraseña incorrectos")
                return render_template("/pages/login.html", captcha=new_captcha_dict)
        return render_template("/pages/login.html", captcha=new_captcha_dict)


# Registro de usuario
@app.route("/register", methods=["POST"])
def registerUser():
    new_captcha_dict = captcha.create()
    cur = mysql.connection.cursor()
    try:
        if request.method == "POST":
            c_hash = request.form.get('captcha-hash')
            c_text = request.form.get('captcha-text')
            if captcha.verify(c_hash, c_text) is False:
                flash("Captcha incorrecto")
                return render_template("/pages/login.html", captcha=new_captcha_dict)
            name = request.form["name"]
            email = request.form["email"]
            password = generate_password_hash(request.form["password"])
            phone = request.form["phone"]
            role = request.form["role"]
            cur.execute(
                "INSERT INTO clientes (nombreCliente, telefono) VALUES (%s, %s)",
                (name, phone),)
            idCliente = cur.lastrowid 
            cur.execute(
                "INSERT INTO usuarios (email, password, rol, idClienteFK) VALUES (%s, %s, %s, %s)",
                (email, password, role, idCliente),)
            cur.execute(
                "SELECT * FROM usuarios where email = %s",
                (email,),)
            user = cur.fetchone()
            mysql.connection.commit()
            cur.close()
            session["user"] = user
            return redirect(url_for("cliente_dashboard"))
    except(Exception) as error:
        if "Duplicate entry" in str(error):
            flash("El correo ya está registrado")
            return redirect(url_for("login"))
        elif "email" in str(error):
            flash("El correo no es válido")
            return redirect(url_for("login"))
        elif "phone" in str(error):
            flash("El teléfono no es válido")
            return redirect(url_for("login"))
        elif "name" in str(error):
            flash("El nombre no es válido")
            return redirect(url_for("login"))
        elif "password" in str(error):
            flash("La contraseña no es válida")
            return redirect(url_for("login"))
    finally:
        cur.close()
        return redirect(url_for("login"))
    


# Registro de admin
@app.route("/registroAdmin", methods=["POST", "GET"])
def registerAdmin():
    active_user = session.get("user")
    if active_user and active_user[4] != "administrador":
        return redirect(url_for("login"))
    if request.method == "POST":
        nombre = request.form["name"]
        apellidoP = request.form["apellidoP"]
        apellidoM = request.form["apellidoM"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        puesto = request.form["puesto"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO empleado (nombreEmpleado, puesto, apellidoP, apellidoM) VALUES (%s, %s, %s, %s)",
            (nombre, puesto, apellidoP, apellidoM),)
        idEmpleado = cur.lastrowid 
        cur.execute(
            "INSERT INTO usuarios (usuario, contraseña, rol, idEmpleadoFK) VALUES (%s, %s, %s, %s)",
            (email, password, role, idEmpleado),)
        mysql.connection.commit()  
        cur.close() 
        flash("Usuario registrado con éxito")
        return redirect(url_for("registerAdmin"))
    return render_template("/admin/registerAdmin.html")


# Logout
@app.route("/logout", methods=["POST"])
def logout():
    if session.get("user") is not None:
        session.clear()
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

@app.route("/checkSession")
def checkSession():
    session_items = {key: session[key] for key in session.keys()}
    return jsonify(session_items)
    if user is not None:
        return jsonify({user})
    else:
        return redirect(url_for("login"))