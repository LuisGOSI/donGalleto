from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from database.admin import proveedorCRUD
from database import inventarioDeGalletas
from database import TiendaGalletas
from db import app,mysql 

if __name__ == "__main__":
    app.run(debug=True)

load_dotenv()
proveedorCRUD.registerProveedor
inventarioDeGalletas.get_InveGalletas
#! ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////// Logica de sesiones de la app ///////////////////////////////////////////////////////////////////////
#! ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@app.route("/login", methods=["GET", "POST"])
def login():
    user = session.get("user")
    if user is not None:
        if user[4] == "cliente":
            return redirect(url_for("cliente_dashboard"))
        elif user[4] == "administrador":
            return redirect(url_for("admin_dashboard"))
        elif user[4] == "produccion":
            return redirect(url_for("produccion_dashboard"))
        elif user[4] == "vendedor":
            return redirect(url_for("ventas_dashboard"))
    else:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios where email = %s", (email,))
            userDb = cur.fetchone()
            print(userDb)
            cur.close()
            if userDb and check_password_hash(userDb[3], password):
                session["user"] = userDb
                role = userDb[4]
                if role == "administrador":
                    return redirect(url_for("admin_dashboard"))
                elif role == "produccion":
                    return redirect(url_for("produccion_dashboard"))
                elif role == "vendedor":
                    return redirect(url_for("ventas_dashboard"))
                else:
                    return redirect(url_for("cliente_dashboard"))
            else:
                return render_template(
                    "/pages/login.html"
                )  # Si falla la autenticación, recarga el login
        return render_template(
            "/pages/login.html"
        )  # Si es GET, muestra el formulario de login


# Registro de usuario
@app.route("/register", methods=["POST"])
def registerUser():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        phone = request.form["phone"]
        role = request.form["role"]
        cur = mysql.connection.cursor()
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
        session.pop("user")
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


#! ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////// Rutas de la app ///////////////////////////////////////////////////////////////////////
#! ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@app.route("/")
def home():
    return render_template("/pages/home.html")


@app.route("/admin")
def admin_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] != "administrador":
        return redirect(url_for("login"))
    return render_template("/admin/admin_dashboard.html")


@app.route("/produccion")
def produccion_dashboard():
    return render_template("/production/baseProduccion/baseProduccion.html", is_base_template=True)


@app.route('/gestion-insumos')
def gestion_insumos():
    cur = mysql.connection.cursor()
    # consulta para traer los prov
    cur.execute("SELECT idProveedor, nombreProveedor FROM proveedores")
    proveedores = cur.fetchall()
    # cargar los insumos
    cur.execute("""
        SELECT 
            i.idInsumo, 
            i.nombreInsumo, 
            i.unidadMedida, 
            COALESCE(pi.precioProveedor, 'No asignado') AS precioProveedor, 
            COALESCE(p.nombrePresentacion, 'No asignado') AS nombrePresentacion, 
            COALESCE(pr.nombreProveedor, 'No asignado') AS nombreProveedor
        FROM insumos i
        LEFT JOIN presentacionesinsumos p ON i.idInsumo = p.idInsumoFK
        LEFT JOIN proveedoresinsumos pi ON p.idPresentacion = pi.idPresentacionFK
        LEFT JOIN proveedores pr ON pi.idProveedorFK = pr.idProveedor
    """)
    insumos = cur.fetchall()
    cur.close()
    return render_template('/production/gestionInsumos.html', proveedores=proveedores, insumos=insumos, is_base_template=False)


@app.route("/inventario-insumos")
def insumos_inventory():
    cur = mysql.connection.cursor()
    # consulta para traer los prov
    cur.execute("SELECT idProveedor, nombreProveedor FROM proveedores")
    proveedores = cur.fetchall()
    # cargar los insumos
    cur.execute("""
        SELECT 
            i.idInsumo, 
            i.nombreInsumo, 
            i.unidadMedida, 
            i.cantidadInsumo, 
            COALESCE(p.nombrePresentacion, 'No asignado') AS nombrePresentacion, 
            COALESCE(pr.nombreProveedor, 'No asignado') AS nombreProveedor
        FROM insumos i
        LEFT JOIN presentacionesinsumos p ON i.idInsumo = p.idInsumoFK
        LEFT JOIN proveedoresinsumos pi ON p.idPresentacion = pi.idPresentacionFK
        LEFT JOIN proveedores pr ON pi.idProveedorFK = pr.idProveedor
    """)
    insumos = cur.fetchall()
    cur.close()
    return render_template('/production/InveInsumos.html', proveedores=proveedores, insumos=insumos, is_base_template=False)


@app.route("/proveedores")
def proveedores():
    return render_template('/production/Proveedores.html', is_base_template = False)


@app.route("/sobreNosotros")
def about_us():
    user = session.get("user")
    if user is not None:
        return render_template("pages/about_us.html", user=user)
    else:
        return render_template("pages/about_us.html", user=None)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("pages/error404.html"), 404

#! /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////// Rutas logicas ///////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#! ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////// Rutas de prueba ///////////////////////////////////////////////////////////////////////
#! //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@app.route("/test")
def test():
    return render_template("/pages/test.html")


@app.route("/ventas")
def ventas_dashboard():
    return "Bienvenido al panel de ventas"

@app.route("/cliente")
def cliente_dashboard():
    user = session.get("user")
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM galletas')
    data = cur.fetchall()
    cur.close()
    print(data)
    return render_template('/client/Cliente.html', is_base_template = False,user=user,data=data)


@app.route("/historico")
def historico_dashboard():
    user = session.get("user")
    return render_template('/client/Historico.html', is_base_template = False,user=user)
    


# Checar sesion
@app.route("/checkSession", methods=["POST"])
def checkSession():
    user_active = session.get("user")
    if user_active is not None:
        return render_template("/pages/test.html", user=user_active)
    else:
        return render_template("/pages/test.html", user=user_active)


def get_empleados():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT e.idEmpleado, e.nombreEmpleado, e.apellidoP, e.apellidoM, e.puesto, 
        u.usuario, u.rol 
        FROM empleado e
        JOIN usuarios u ON e.idEmpleado = u.idEmpleadoFK
    """)
    empleados = cur.fetchall()
    cur.close()
    return empleados

