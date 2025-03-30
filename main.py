from flask import render_template, request, redirect, url_for, session
from database.production import insumosCRUD, gestionRecetas
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
    cur.execute("""
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
    """)
    formatos_receta = cur.fetchall()
    cur.close()
    return render_template('/production/gestionInsumos.html', insumos=insumos, presentaciones=presentaciones, proveedores=proveedores, 
                           formatos_receta=formatos_receta, is_base_template=False)


@app.route("/inventario-insumos")
def insumos_inventory():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    hoy = datetime.now().date()
    insumos = inventarioDeInsumos.getInvInsumosTabla()
    print(insumos)
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            inv.idInventarioInsumo as id_lote,
            ins.nombreInsumo as nombre,
            inv.cantidad as cantidad_proxima_caducar,
            inv.fechaCaducidad as fecha_caducidad,
            ins.unidadMedida as unidad_medida,
            DATEDIFF(inv.fechaCaducidad, CURDATE()) as dias_restantes,
            inv.estadoLote as estado
        FROM inventarioInsumos as inv
        JOIN insumos ins ON inv.idInsumoFK = ins.idInsumo
        WHERE inv.cantidad > 0
        ORDER BY dias_restantes ASC
    """)
    insumos_raw = cursor.fetchall()
    for insumo in insumos_raw:
        fecha_caducidad_raw = insumo[3]  # índice 3 corresponde a fecha_caducidad
        id_lote = insumo[0]             # índice 0 corresponde a id_lote
        estado = insumo[6]              # índice 6 corresponde a estado
        if fecha_caducidad_raw:
            if isinstance(fecha_caducidad_raw, str):
                fecha_caducidad = datetime.strptime(fecha_caducidad_raw, "%Y-%m-%d").date()
            else:
                fecha_caducidad = fecha_caducidad_raw
            dias_restantes = (fecha_caducidad - hoy).days
            if dias_restantes < 0 and estado != "Caducado":
                cursor.execute("""
                    UPDATE inventarioInsumos
                    SET estadoLote = 'Caducado' 
                    WHERE idInventarioInsumo = %s
                """, (id_lote,))
                mysql.connection.commit()
    cursor.execute("""
        SELECT 
            inv.idInventarioInsumo as id_lote,
            ins.nombreInsumo as nombre,
            inv.cantidad as cantidad_proxima_caducar,
            inv.fechaCaducidad as fecha_caducidad,
            ins.unidadMedida as unidad_medida,
            DATEDIFF(inv.fechaCaducidad, CURDATE()) as dias_restantes,
            inv.estadoLote as estado
        FROM inventarioInsumos as inv
        JOIN insumos ins ON inv.idInsumoFK = ins.idInsumo
        WHERE inv.cantidad > 0
        ORDER BY dias_restantes ASC
    """)
    lotesResumen = []
    proximos_caducar = []
    for row in cursor.fetchall():
        lote = {
            'id_lote': row[0],
            'nombre': row[1],
            'cantidad_proxima_caducar': row[2],
            'fecha_caducidad': row[3],
            'unidad_medida': row[4],
            'dias_restantes': row[5],
            'estado': row[6]
        }
        lotesResumen.append(lote)
        if lote['dias_restantes'] is not None and lote['dias_restantes'] >= 0:
            proximos_caducar.append(lote)
    cursor.close()
    return render_template(
        "/production/inveInsumos.html", 
        insumos=insumos, 
        lotesResumen=lotesResumen, 
        proximos_caducar=proximos_caducar,  
        is_base_template=False
    )

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
    cur.execute("SELECT idInsumo, nombreInsumo, unidadMedida FROM insumos ORDER BY nombreInsumo")
    insumos = cur.fetchall()
    
    # Obtener formatos disponibles
    cur.execute("SELECT idFormato, nombreFormato FROM formatosRecetas ORDER BY nombreFormato")
    formatos = cur.fetchall()
    
    cur.close()
    
    return render_template(
        '/production/Recetas.html', 
        is_base_template=False,
        galletas=galletas,
        insumos=insumos,
        formatos=formatos
    )


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