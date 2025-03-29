from flask import render_template, request, redirect, url_for, session
from database.production import insumosCRUD
from database.admin import proveedorCRUD, clientesCRUD, dashboard
from database.usuario import usuariosCRUD
from database.production import inventarioDeGalletas, inventarioDeInsumos
from database.cliente import clientes
from database.cookies import cookies
from datetime import datetime
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
    presentaciones=dashboard.getPresentaciones()
    ganancias=dashboard.getGanancias()
    galletas=dashboard.getGalletasTop()
    return render_template("/admin/admin_dashboard.html", presentaciones=presentaciones, ganancias=ganancias, galletas=galletas)

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

@app.route("/solicitudProduccion")
def solicitudProduccion_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "ventas"]:
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM galletas')
    galletas = cur.fetchall()
    cur.close()
    return render_template("/production/SolicitudProduccion.html", is_base_template=False, user=user,galletas=galletas)

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
    hoy = datetime.today().date()
    insumos = inventarioDeInsumos.getInvInsumosTabla()
    return render_template("/production/inveInsumos.html", insumos=insumos, is_base_template=False)


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
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM galletas')
    galletas = cur.fetchall()
    cur.close()
    return render_template('/production/Produccion.html', is_base_template = False,user=user,galletas=galletas)


@app.route("/cliente")
def cliente_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    data = cookies.getCookies()
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
    idCliente = user[0]
    # Obtener el nombre del cliente de la tabla de clientes
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombreCliente FROM clientes WHERE idCliente = %s", (idCliente,))
    resultado_cliente = cur.fetchone()
    nombreCliente = resultado_cliente[0] if resultado_cliente else "Cliente"
    # Consulta para histórico de compras
    cur.execute("SELECT * FROM v_historicoCompras WHERE idCliente = %s", (idCliente,))
    column_names = [column[0] for column in cur.description]
    historico_compras = []
    for row in cur.fetchall():
        compra_dict = {}
        for i, col_name in enumerate(column_names):
            compra_dict[col_name] = row[i]
        historico_compras.append(compra_dict)
    cur.close()
    # Verificar si hay compras
    historico = len(historico_compras) > 0
    
    return render_template('/client/Historico.html', 
                           is_base_template=False, 
                           user=user, 
                           historico_compras=historico_compras,
                           historico=historico,
                           nombreCliente=nombreCliente)

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

@app.route("/ventas")
def ventas_dashboard():
    return render_template("/sales/sales.html")


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

