from flask import render_template, request, redirect, url_for, session
from database.production import insumosCRUD
from database.admin import proveedorCRUD, clientesCRUD
from database.usuario import usuariosCRUD
from database.production import inventarioDeGalletas
from database.cliente import clientes
from db import app,mysql 
from sessions import *

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

@app.route("/gestionUsuarios")
def usuarios_dashboard():
    user = session.get("user")
    return render_template('/usuario/Usuario.html', is_base_template = False, user=user)


@app.route("/produccion")
def produccion_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    return render_template("/production/baseProduccion/baseProduccion.html", is_base_template=True)


@app.route('/gestion-insumos')
def gestion_insumos():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute("SELECT idInsumo, nombreInsumo, unidadMedida FROM insumos")
    insumos = cur.fetchall()
    cur.execute("""
        SELECT 
            i.idInsumo, 
            i.nombreInsumo, 
            p.idPresentacion, 
            p.nombrePresentacion, 
            p.cantidadBase, 
            pr.nombreProveedor, 
            pi.precioProveedor
        FROM 
            insumos i
        INNER JOIN 
            presentacionesinsumos p ON i.idInsumo = p.idInsumoFK
        LEFT JOIN 
            proveedoresinsumos pi ON p.idPresentacion = pi.idPresentacionFK
        LEFT JOIN 
            proveedores pr ON pi.idProveedorFK = pr.idProveedor
    """)
    presentaciones = cur.fetchall()
    cur.execute("SELECT idProveedor, nombreProveedor FROM proveedores")
    proveedores = cur.fetchall()
    cur.close()
    return render_template('/production/gestionInsumos.html', insumos=insumos, presentaciones=presentaciones, proveedores=proveedores, is_base_template=False)


@app.route("/inventario-insumos")
def insumos_inventory():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute("SELECT idProveedor, nombreProveedor FROM proveedores")
    proveedores = cur.fetchall()
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
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    return render_template('/production/Proveedores.html', is_base_template = False)

@app.route("/moduloProduccion")
def moduloProduccion():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    return render_template('/production/Produccion.html', is_base_template = False,user=user)


@app.route("/cliente")
def cliente_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM galletas')
    data = cur.fetchall()
    cur.close()
    print(data)
    return render_template('/client/Cliente.html', is_base_template = False,user=user,data=data)

@app.route("/clientes")
def clientes():
    if "user" not in session:
        return redirect(url_for("login"))
    
    active_user = session.get("user")

    if active_user[4] != "administrador":
        return render_template("pages/error404.html"), 404

    status = request.args.get("status", default=1, type=int)  # Por defecto activos
    
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT 
            c.idCliente,
            c.nombreCliente,
            c.telefono,
            u.email,
            u.rol,
            u.status
        FROM 
            clientes c
        INNER JOIN 
            usuarios u ON c.idCliente = u.idClienteFK
        WHERE 
            u.status = %s;
    """, (status,))
    
    clientes = cur.fetchall()
    cur.close()
    
    return render_template('/admin/gestionClientes.html', clientes=clientes, status=status, is_base_template=False)


@app.route("/receta")
def receta():
    if "user" not in session:
        return redirect(url_for("login"))
    active_user = session.get("user")
    if active_user[4] not in ["produccion", "administrador"]:
        return render_template("pages/error404.html"), 404
    return render_template('/production/Recetas.html', is_base_template = False)


@app.route("/carrito")
def carrito_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    return render_template('/client/Carrito.html', is_base_template = False,user=user)


@app.route("/historico")
def historico_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    return render_template('/client/Historico.html', is_base_template = False,user=user)


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

#! ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////// Rutas de prueba ///////////////////////////////////////////////////////////////////////
#! //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@app.route("/test")
def test():
    return render_template("/pages/test.html")


@app.route("/ventas")
def ventas_dashboard():
    return render_template("/sales/sales.html")

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