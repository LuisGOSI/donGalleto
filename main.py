from flask import render_template, request, redirect, url_for, session
from database.production import insumosCRUD, gestionRecetas
from database.admin import proveedorCRUD, clientesCRUD, dashboard
from database.usuario import usuariosCRUD
from database.production import inventarioDeGalletas, inventarioDeInsumos
from database.cliente import clientes
from database.cookies import cookies
from datetime import datetime
from db import app, mysql
from sessions import *
import json

#! ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////// Rutas de la app ///////////////////////////////////////////////////////////////////////
#! ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


@app.route("/")
def home():
    inventarioDeGalletas.getInveGalletas()
    return render_template("/pages/home.html")


@app.route("/admin")
def admin_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] != "administrador":
        return redirect(url_for("login"))
    presentaciones = dashboard.getPresentaciones()
    ganancias = dashboard.getGanancias()
    galletas = dashboard.getGalletasTop()
    return render_template(
        "/admin/admin_dashboard.html",
        presentaciones=presentaciones,
        ganancias=ganancias,
        galletas=galletas,
    )


@app.route("/gestionUsuarios")
def usuarios_dashboard():
    user = session.get("user")
    return render_template("/usuario/Usuario.html", is_base_template=False, user=user)


@app.route("/produccion")
def produccion_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    return render_template(
        "/production/baseProduccion/baseProduccion.html", is_base_template=True
    )


@app.route("/solicitudProduccion")
def solicitudProduccion_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "ventas"]:
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM galletas")
    galletas = cur.fetchall()
    cur.close()
    return render_template(
        "/production/SolicitudProduccion.html",
        is_base_template=False,
        user=user,
        galletas=galletas,
    )


@app.route("/gestion-insumos")
def gestion_insumos():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute("SELECT idInsumo, nombreInsumo, unidadMedida FROM insumos")
    insumos = cur.fetchall()
    cur.execute(
        """
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
    """
    )
    presentaciones = cur.fetchall()
    cur.execute("SELECT idProveedor, nombreProveedor FROM proveedores")
    proveedores = cur.fetchall()
    cur.execute(
        """
        SELECT 
            fr.idFormato,
            i.nombreInsumo,
            i.unidadMedida,
            fr.nombreFormato,
            ifr.cantidadConvertida
        FROM 
            formatosRecetas fr
        JOIN 
            insumoFormatos ifr ON fr.idFormato = ifr.idFormatoFK
        JOIN 
            insumos i ON ifr.idInsumoFK = i.idInsumo
        ORDER BY 
            i.nombreInsumo, fr.nombreFormato
    """
    )
    formatos_receta = cur.fetchall()
    cur.close()
    return render_template(
        "/production/gestionInsumos.html",
        insumos=insumos,
        presentaciones=presentaciones,
        proveedores=proveedores,
        formatos_receta=formatos_receta,
        is_base_template=False,
    )


@app.route("/inventario-insumos")
def insumos_inventory():
    user = session.get("user")
    if not user or user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    inventarioDeInsumos.actualizar_estados_caducidad()
    insumos = inventarioDeInsumos.getInvInsumosTabla()
    lotesResumen, proximos_caducar = inventarioDeInsumos.getInsumosResumen()
    return render_template(
        "/production/inveInsumos.html",
        insumos=insumos,
        lotesResumen=lotesResumen,
        proximos_caducar=proximos_caducar,
        is_base_template=False,
    )


@app.route("/proveedores")
def proveedores():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    return render_template("/production/Proveedores.html", is_base_template=False)


@app.route("/moduloProduccion")
def moduloProduccion():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM galletas")
    galletas = cur.fetchall()
    cur.close()
    return render_template(
        "/production/Produccion.html",
        is_base_template=False,
        user=user,
        galletas=galletas,
    )


# Rutas para el modulo de clientes / Sistema de carrito
@app.route("/cliente")
def cliente_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    data = cookies.getCookies()
    return render_template(
        "/client/Cliente.html", is_base_template=False, user=user, data=data
    )


@app.route("/detalle_producto", methods=["GET", "POST"])
def detalle_producto():
    if session.get("user") is None:
        return redirect(url_for("login"))

    # Usar request.form para los datos enviados por POST
    galleta_json = request.form.get("galleta")  # Obtener la galleta del formulario POST
    print("JSON recibido:", galleta_json)

    galleta = json.loads(galleta_json) if galleta_json else None
    print(f"Galleta: {galleta}")

    return render_template(
        "/client/DetalleProducto.html", is_base_template=False, galleta=galleta
    )


@app.route("/agregar_carrito/<int:id>", methods=["POST"])
def agregar_al_carrito(id):
    # Se obtiene la cantidad del formulario
    cantidad = int(request.form.get("cantidad", 1))
    tipo_venta = request.form.get(
        "saleType", "unidad"
    )  # Obtener el tipo de venta del formulario
    # Se obtienen las galletas del catalago
    data = cookies.getCookies()

    producto = next((item for item in data if item[0] == id), None)
    if not producto:
        return redirect(url_for("cliente_dashboard"))

    if "carrito" not in session:
        session["carrito"] = {}

    carrito = session["carrito"]

    # Generamos una clave única usando ID y tipo de venta
    clave_carrito = f"{id}_{tipo_venta}"

    if clave_carrito in carrito:
        # Si ya existe con el mismo tipo de venta, sumamos la cantidad
        carrito[clave_carrito]["cantidad"] += cantidad
    else:
        # Si es un nuevo tipo de venta, lo agregamos como un nuevo producto en el carrito
        carrito[clave_carrito] = {
            "id": producto[0],
            "nombre": producto[1],
            "precio": producto[2],
            "cantidad": cantidad,
            "tipo_venta": tipo_venta,
        }

    print("Carrito actualizado:", carrito)

    session.modified = True

    return redirect(url_for("cliente_dashboard"))


# Fin de rutas para el modulo de clientes / Sistema de carrito


@app.route("/clientes")
def clientes():
    if "user" not in session:
        return redirect(url_for("login"))
    active_user = session.get("user")
    if active_user[4] != "administrador":
        return render_template("pages/error404.html"), 404
    status = request.args.get("status", default=1, type=int)  # Por defecto activos
    cur = mysql.connection.cursor()
    cur.execute(
        """
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
    """,
        (status,),
    )
    clientes = cur.fetchall()
    cur.close()
    return render_template(
        "/admin/gestionClientes.html",
        clientes=clientes,
        status=status,
        is_base_template=False,
    )


@app.route("/receta")
def receta():
    if "user" not in session:
        return redirect(url_for("login"))
    active_user = session.get("user")
    if active_user[4] not in ["produccion", "administrador"]:
        return render_template("pages/error404.html"), 404

    cur = mysql.connection.cursor()

    # Obtener galletas para el select
    cur.execute("SELECT idGalleta, nombreGalleta FROM galletas ORDER BY nombreGalleta")
    galletas = cur.fetchall()

    # Obtener insumos para el select
    cur.execute(
        "SELECT idInsumo, nombreInsumo, unidadMedida FROM insumos ORDER BY nombreInsumo"
    )
    insumos = cur.fetchall()

    # Obtener formatos disponibles
    cur.execute(
        "SELECT idFormato, nombreFormato FROM formatosRecetas ORDER BY nombreFormato"
    )
    formatos = cur.fetchall()

    cur.close()

    return render_template(
        "/production/Recetas.html",
        is_base_template=False,
        galletas=galletas,
        insumos=insumos,
        formatos=formatos,
    )


@app.route("/carrito")
def carrito_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")

    if "carrito" not in session or not session["carrito"]:
        carrito = {}
    else:
        carrito = session["carrito"]

    total_items = sum(
        item["cantidad"] for item in carrito.values()
    )  # Total de productos
    total_precio = sum(
        item["precio"] * item["cantidad"] for item in carrito.values()
    )  # Total a pagar

    return render_template(
        "/client/Carrito.html",
        is_base_template=False,
        user=user,
        total_items=total_items,
        total_precio=total_precio,
        carrito=carrito,
    )


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

    return render_template(
        "/client/Historico.html",
        is_base_template=False,
        user=user,
        historico_compras=historico_compras,
        historico=historico,
        nombreCliente=nombreCliente,
    )


@app.route("/ventas")
def ventas_dashboard():
    user = session.get("user")
    if not user or user[4] not in ["ventas", "administrador"]:
        return redirect(url_for("login"))
    user = session.get("user")
    data = cookies.getCookies()
    return render_template("sales/baseVentas/baseVenta.html", data=data, user=user, is_base_template=True)

@app.route("/corteVentas")
def corteVentas():
    user = session.get("user")
    return render_template("/sales/corteVenta.html", user=user)

@app.route("/moduloVentas")	
def moduloVentas():
    user = session.get("user")
    data = cookies.getCookies()
    return render_template("/sales/sales.html", data=data, user=user,)


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


def get_empleados():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT e.idEmpleado, e.nombreEmpleado, e.apellidoP, e.apellidoM, e.puesto, 
        u.usuario, u.rol 
        FROM empleado e
        JOIN usuarios u ON e.idEmpleado = u.idEmpleadoFK
    """
    )
    empleados = cur.fetchall()
    cur.close()
    return empleados
