from flask import render_template, request, redirect, url_for, session
from database.production import insumosCRUD, gestionRecetas, solicitudProduccion
from database.admin import proveedorCRUD, clientesCRUD, dashboard
from database.usuario import usuariosCRUD
from database.production import inventarioDeGalletas, inventarioDeInsumos, moduloProduccion
from database.cliente import clientes
from database.cookies import cookies
from database.sales import ventas, corteVenta
from datetime import datetime
from db import app, mysql, mail
from sessions import *
from pdf_ticket import *
import json,logging
from flask_mail import Message

#! ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#! /////////////////////////////////////////////////////////////////////// Rutas de la app ///////////////////////////////////////////////////////////////////////
#! ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


@app.route("/")
def home():
    return render_template("/pages/home.html")


@app.route("/dashboard")
def admin_dashboard():
    if "user" not in session:
        app.logger.error('Usuario desconocido intento acceder al dashboard, acceso denegado')
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["administrador"]:
        app.logger.warning(f'El usuario con correo "{user[2]}" intento acceder al dashboard, acceso denegado')
        return render_template("pages/error404.html"), 404
    presentaciones = dashboard.getPresentaciones()
    ganancias = dashboard.getGanancias()
    galletas = dashboard.getGalletasTop()
    inversion=dashboard.getInversionGalletas()
    recomendada=dashboard.getGalletaRecomendad()
    app.logger.debug(f'rol verificado, el usuario con correo "{user[2] }" accedio correctamente al dashboard')
    return render_template(
        "/admin/admin_dashboard.html",
        presentaciones=presentaciones,
        ganancias=ganancias,
        galletas=galletas,
        user=user,
        inversion=inversion,
        recomendada=recomendada,
    )


@app.route("/gestionUsuarios")
def usuarios_dashboard():
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["administrador"]:
        return render_template("pages/error404.html"), 404
    return render_template("/usuario/Usuario.html", is_base_template=False, user=user)


@app.route("/produccion")
def produccion_dashboard():
    if session.get("user") is None:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["produccion"]:
        return render_template("pages/error404.html"), 404
    return render_template(
        "/production/baseProduccion/baseProduccion.html",
        is_base_template=True,
        user=user,
    )


@app.route("/solicitudProduccion")
def solicitudProduccion_dashboard():
    if session.get("user") is None:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["produccion", "ventas"]:
        return render_template("pages/error404.html"), 404
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
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["produccion"]:
        return render_template("pages/error404.html"), 404
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
        user=user,
    )


@app.route("/inventario-insumos")
def insumos_inventory():
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["produccion"]:
        return render_template("pages/error404.html"), 404
    inventarioDeInsumos.actualizar_estados_caducidad()
    insumos = inventarioDeInsumos.getInvInsumosTabla()
    lotesResumen, proximos_caducar = inventarioDeInsumos.getInsumosResumen()
    return render_template(
        "/production/inveInsumos.html",
        insumos=insumos,
        lotesResumen=lotesResumen,
        proximos_caducar=proximos_caducar,
        is_base_template=False,
        user=user,
    )


@app.route("/moduloProduccion")
def moduloProduccion():
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["produccion"]:
        return render_template("pages/error404.html"), 404
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


# Rutas para el modulo de clientes / Sistema de carrito /Cambio de contraseña
@app.route("/cambiar_contrasena", methods=["GET", "POST"])
def cambiar_contrasena():
    if session.get("user") is None:
        return render_template("pages/error404.html"), 404
    user=session.get("user")
    return render_template("/client/cambiarPassword.html", is_base_template=False, )

@app.route("/gestionClientes")
def cliente_dashboard():
    if session.get("user") is None:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    data = cookies.getCookies()
    return render_template(
        "/client/Cliente.html", is_base_template=False, user=user, data=data
    )


@app.route("/detalle_producto", methods=["GET", "POST"])
def detalle_producto():
    user = session.get("user")
    if session.get("user") is None:
        return render_template("pages/error404.html"), 404
    galleta_json = request.form.get("galleta") or request.args.get("galleta")
    galleta = json.loads(galleta_json) if galleta_json else None

    return render_template(
        "/client/DetalleProducto.html", is_base_template=False, galleta=galleta,user=user
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
        flash("Error: Producto no encontrado", "error")
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
    flash("✅ Producto agregado al carrito", "success")
    return redirect(url_for("detalle_producto", galleta=json.dumps(producto)))


@app.route("/eliminar_carrito/<int:id>/<tipo_venta>", methods=["POST"])
def eliminar_del_carrito(id, tipo_venta):
    if "carrito" in session:
        carrito = session["carrito"]

        clave = f"{id}_{tipo_venta}"  # Genera la clave en el formato correcto

        if clave in carrito:
            del carrito[clave]  # Elimina el producto del carrito
            session.modified = True  # Guarda los cambios en la sesión
            print(f"Producto eliminado: {clave}")  # Depuración en consola
        else:
            print(f"No se encontró la clave: {clave}")  # Depuración si no lo encuentra

    return redirect(url_for("carrito_dashboard"))  # Volver a la vista del carrito


@app.route("/finalizar_compra", methods=["POST"])
def finalizar_compra():
    user = session.get("user")
    user_id = session.get("user")[6]  # ID del cliente en sesión
    carrito = session.get("carrito")
    total_precio = sum(item["precio"] * item["cantidad"] for item in carrito.values())
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_empleado = 1  # ID de un empleado específico para ventas en línea
    descuento = 0  # Puedes modificar esto si hay descuentos
    tipo_venta = request.form.get("tipo_venta", "online")  # Por defecto online para clientes
    cur = mysql.connection.cursor()

    try:
        # Insertar la venta en la tabla `ventas`
        cur.execute(
            """
            INSERT INTO ventas (idEmpleadoFK, idClienteFK, fechaVenta, descuento, tipoVenta, estadoVenta)
            VALUES (%s, %s, %s, %s, %s,
                    CASE WHEN %s = 'online' THEN 'pendiente' ELSE 'confirmada' END)
            """,
            (id_empleado, user_id, fecha_actual, descuento, tipo_venta, tipo_venta),
        )
        mysql.connection.commit()

        # Obtener el ID de la venta generada
        id_venta = cur.lastrowid
        print(f"✅ ID de la venta generada: {id_venta}")

        # Insertar detalles de la venta en la tabla `detalleventas`
        for key, item in carrito.items():
            print(f"Producto en carrito: {item}")
            id_galleta = key.split("_")[0]  # ID del producto (galleta)
            tipo_venta_detalle = item.get(
                "tipo_venta", "unidad"
            )  # Debe ser 'gramaje', 'paquetes' o 'unidades'
            print(f"Tipo de venta: {tipo_venta_detalle}")

            cur.execute(
                """
                INSERT INTO detalleventas (idVentaFK, idGalletaFK, cantidadVendida, tipoVenta, PrecioUnitarioVendido)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    id_venta,
                    id_galleta,
                    item["cantidad"],
                    tipo_venta_detalle,
                    item["precio"],
                ),
            )
            # Actualizar inventario solo si es venta local (confirmada)
        if tipo_venta == "local":
            for key, item in carrito.items():
                id_galleta = key.split("_")[0]
                cantidad = item["cantidad"]

                # Convertir a unidades si es paquete
                if item["tipo_venta"] == "paquete 1kg":
                    peso_galleta = ventas.revisar_gramaje_por_id(id_galleta)
                    cantidad = round(cantidad * 1000 / peso_galleta)
                elif item["tipo_venta"] == "paquete 700gr":
                    peso_galleta = ventas.revisar_gramaje_por_id(id_galleta)
                    cantidad = round(cantidad * 700 / peso_galleta)

                cur.execute(
                    """
                    UPDATE inventariogalletas 
                    SET cantidadGalletas = cantidadGalletas - %s
                    WHERE idProduccionFK = (SELECT idProduccion FROM produccion WHERE idRecetaFK = (SELECT idReceta FROM recetas WHERE idGalletaFK = %s) LIMIT 1)
                    AND cantidadGalletas >= %s
                    AND estadoLote = 'Disponible'
                    ORDER BY fechaCaducidad ASC
                    LIMIT 1
                    """,
                    (cantidad, id_galleta, cantidad),
                )
        mysql.connection.commit()

        total_items = sum(
        item["cantidad"] for item in carrito.values()
        )

        msg = Message('RECIBO',
        sender='contacto.soydongalleto@gmail.com',
        recipients=[user[2]])  # Accediendo al correo del usuario
        msg.html = render_template(
        "/client/emailVenta.html",
        total_items=total_items,
        total_precio=total_precio,
        carrito=carrito,
        id_venta=id_venta,
        )
        mail.send(msg)



        # Vaciar el carrito después de la compra
        session.pop("carrito")
        flash("Compra finalizada con éxito.", "success")
        flash("Id de tu compra: " + str(id_venta), "success")
        return redirect(url_for("carrito_dashboard"))
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Ocurrió un error al procesar el pedido: {e}", "danger")
        print(f"❌ Error en la compra: {e}")
        return redirect(url_for("carrito_dashboard"))

    finally:
        cur.close()
        

# Fin de rutas para el modulo de clientes / Sistema de carrito


@app.route("/clientes")
def clientes():
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] != "administrador":
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
        user=user,
    )


@app.route("/receta")
def receta():
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["produccion"]:
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

    # Obtener todas las recetas básicas para la tabla principal
    cur.execute(
        """
        SELECT r.idReceta, r.nombreReceta, r.cantidadHorneadas, r.duracionAnaquel, 
        g.nombreGalleta
        FROM recetas r
        JOIN galletas g ON r.idGalletaFK = g.idGalleta
        WHERE r.estatus = 1
        ORDER BY g.nombreGalleta, r.nombreReceta
    """
    )
    recetas = cur.fetchall()

    cur.close()

    return render_template(
        "/production/Recetas.html",
        is_base_template=False,
        galletas=galletas,
        insumos=insumos,
        formatos=formatos,
        recetas=recetas,
        user=user,
    )


@app.route("/carrito")
def carrito_dashboard():
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["cliente"]:
        return render_template("pages/error404.html"), 404

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
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["cliente"]:
        return render_template("pages/error404.html"), 404
    
    idUsuario = user[0]
    # Obtener el id del cliente y nombre de la tabla clientes
    cur = mysql.connection.cursor()
    cur.execute(
        """
    SELECT c.idCliente, c.nombreCliente
    FROM clientes c
    INNER JOIN usuarios u
    ON c.idCliente = u.idClienteFK
    WHERE idUsuario = %s;
    """,
        (idUsuario,),
    )
    resultado_cliente = cur.fetchone()
    
    if resultado_cliente:
        idCliente = resultado_cliente[0]  # Ahora usamos el idCliente de la tabla clientes
        nombreCliente = resultado_cliente[1]
    else:
        return render_template("pages/error404.html"), 404  # Si no hay cliente asociado
    
    # Consulta para histórico de compras
    cur.execute("SELECT * FROM v_historicoCompras where idCliente = %s", (idCliente,))
    print("ID del cliente:", idCliente)
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
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["ventas"]:
        return render_template("pages/error404.html"), 404
    data = cookies.getCookies()
    print("Data de ventas:", data)
    return render_template(
        "sales/baseVentas/baseVenta.html", data=data, user=user, is_base_template=True
    )


@app.route("/moduloVentas")
def moduloVentas():
    if "user" not in session:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] not in ["ventas"]:
        return render_template("pages/error404.html"), 404
    data = cookies.getCookies()
    return render_template(
        "/sales/sales.html", data=data, user=user, is_base_template=False
    )


@app.route("/listadoVentas")
def listadoVentas():
    if "user" not in session:
        return redirect(url_for("login"))
    active_user = session.get("user")
    if active_user[4] not in ["ventas", "administrador"]:
        return render_template("pages/error404.html"), 404
    
    cur = mysql.connection.cursor()
    
    try:
        # Consulta base modificada para calcular correctamente el subtotal
        base_query = """
            SELECT 
                v.idVenta,
                v.fechaVenta,
                v.descuento,
                SUM(
                    CASE 
                        WHEN dv.tipoVenta = 'gramaje' THEN dv.PrecioUnitarioVendido * dv.cantidad_galletas
                        ELSE dv.PrecioUnitarioVendido * dv.cantidadVendida
                    END
                ) AS subtotal,
                SUM(
                    CASE 
                        WHEN dv.tipoVenta = 'gramaje' THEN dv.PrecioUnitarioVendido * dv.cantidad_galletas
                        ELSE dv.PrecioUnitarioVendido * dv.cantidadVendida
                    END
                ) * (1 - v.descuento/100) AS totalVenta,
                GROUP_CONCAT(
                    CONCAT_WS(
                        '||', 
                        g.nombreGalleta, 
                        dv.tipoVenta, 
                        dv.cantidadVendida,
                        dv.PrecioUnitarioVendido,
                        CASE 
                            WHEN dv.tipoVenta = 'gramaje' THEN dv.PrecioUnitarioVendido * dv.cantidad_galletas
                            ELSE dv.PrecioUnitarioVendido * dv.cantidadVendida
                        END
                    ) SEPARATOR ';;'
                ) AS productos
            FROM ventas v
            JOIN detalleventas dv ON v.idVenta = dv.idVentaFK
            JOIN galletas g ON dv.idGalletaFK = g.idGalleta
            {where_clause}
            AND v.estadoVenta = 'confirmada'
            GROUP BY v.idVenta
            ORDER BY v.fechaVenta DESC
            LIMIT 100
        """

        
        # Obtener parámetros de filtro
        filter_type = request.args.get('filter_type')
        filter_value = request.args.get('filter_value')
        
        where_clause = "WHERE 1=1"
        params = []
        
        if filter_type and filter_value:
            if filter_type == 'day':
                where_clause += " AND DATE(v.fechaVenta) = %s"
                params.append(filter_value)
            elif filter_type == 'week':
                year, week = filter_value.split('-W')
                where_clause += """
                    AND YEAR(v.fechaVenta) = %s 
                    AND WEEK(v.fechaVenta, 3) = %s
                """
                params.extend([year, week])
            elif filter_type == 'month':
                year, month = filter_value.split('-')
                where_clause += """
                    AND YEAR(v.fechaVenta) = %s 
                    AND MONTH(v.fechaVenta) = %s
                """
                params.extend([year, month])
            elif filter_type == 'range':
                start_date, end_date = filter_value.split('|')
                where_clause += " AND DATE(v.fechaVenta) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
        
        # Construir la consulta final
        final_query = base_query.format(where_clause=where_clause)
        
        # Ejecutar consulta con parámetros
        cur.execute(final_query, params)
        
        ventas = []
        for row in cur.fetchall():
            # Procesar productos
            productos_raw = row[5].split(';;') if row[5] else []
            productos = []
            for prod in productos_raw:
                partes = prod.split('||')
                productos.append({
                    'nombre': partes[0],
                    'tipoVenta': partes[1],
                    'cantidad': int(partes[2]),  # cantidadVendida
                    'precio': float(partes[3]),    # precio unitario
                    'total_producto': float(partes[4])  # calculado según tipo
                })
            
            ventas.append({
                'idVenta': row[0],
                'fechaVenta': row[1],
                'descuento': float(row[2]),
                'subtotal': float(row[3]),
                'totalVenta': float(row[4]),
                'productos': productos
            })
            
        return render_template("/sales/listadoVentas.html", 
                             user=session.get("user"),
                             ventas=ventas,
                             is_base_template=False)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template("/sales/listadoVentas.html", 
                             user=session.get("user"),
                             ventas=[],
                             error=str(e))
    finally:
        cur.close()

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


@app.route('/enviar-correo')
def enviar_correo():
    msg = Message('¡Hola desde Flask!',
                  sender='contacto.soydongalleto@gmail.com',
                  recipients=['alberto.rt@outlook.com'])
    msg.body = 'Este es un mensaje enviado desde una app Flask.'
    mail.send(msg)
    return 'Correo enviado'



LOG_FILENAME = 'temp\logs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)