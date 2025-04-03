from flask import request, redirect, url_for, flash, jsonify, session   
from db import app, mysql

def getInvInsumosTabla():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM vistaInventarioInsumos")
    insumosTabla = cursor.fetchall()
    cursor.close()
    return insumosTabla


def obtener_insumos():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            idInsumo, 
            nombreInsumo,
            unidadMedida
        FROM insumos
    """)
    insumos = cursor.fetchall()
    cursor.close()
    return insumos


def obtener_presentaciones_por_insumo(id_insumo):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            p.idPresentacion, 
            p.nombrePresentacion, 
            p.cantidadBase, 
            i.unidadMedida
        FROM presentacionesinsumos p
        JOIN insumos i ON p.idInsumoFK = i.idInsumo
        WHERE p.idInsumoFK = %s
    """, (id_insumo,))
    presentaciones = cursor.fetchall()
    cursor.close()
    return presentaciones

def actualizar_estados_caducidad():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE inventarioinsumos
        SET estadoLote = 'Caducado'
        WHERE fechaCaducidad < CURDATE() AND estadoLote != 'Caducado'
    """)
    mysql.connection.commit()
    cursor.close()


def getInsumosResumen():
    cur = mysql.connection.cursor()
    cur.execute("""
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
    for row in cur.fetchall():
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
    cur.close()
    return lotesResumen, proximos_caducar


@app.route('/getInsumos')
def get_insumos():
    insumos = obtener_insumos()
    return jsonify([{
        'idInsumo': insumo[0],    
        'nombreInsumo': insumo[1],
        'unidadMedida': insumo[2] 
    } for insumo in insumos])


@app.route('/getProveedores')
def get_proveedores():
    cur = mysql.connection.cursor()
    cur.execute("SELECT idProveedor, nombreProveedor FROM proveedores")
    proveedores = cur.fetchall()
    print(proveedores)  # Verifica que los proveedores se obtienen correctamente
    cur.close()
    return jsonify([{
        'idProveedor': proveedor[0],
        'nombreProveedor': proveedor[1]
    } for proveedor in proveedores])    

@app.route('/getPresentacionesPorInsumoYProveedor/<int:idInsumo>/<int:idProveedor>')
def get_presentaciones_por_insumo_y_proveedor(idInsumo, idProveedor):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.idPresentacion, 
            p.nombrePresentacion, 
            ps.precioProveedor, 
            p.cantidadBase, 
            i.unidadMedida
        FROM presentacionesinsumos p
        JOIN proveedoresinsumos ps ON p.idPresentacion = ps.idPresentacionFK
        JOIN insumos i ON p.idInsumoFK = i.idInsumo
        WHERE p.idInsumoFK = %s AND ps.idProveedorFK = %s
    """, (idInsumo, idProveedor))
    presentaciones = cur.fetchall()
    cur.close()
    return jsonify([{
        'idPresentacion': presentacion[0],
        'nombrePresentacion': presentacion[1],
        'precioProveedor': presentacion[2],
        'cantidadBase': presentacion[3],
        'unidadMedida': presentacion[4]
    } for presentacion in presentaciones])


@app.route('/getPresentacionesPorInsumo/<int:id_insumo>')
def get_presentaciones_por_insumo(id_insumo):
    presentaciones = obtener_presentaciones_por_insumo(id_insumo)
    return jsonify([{
        'idPresentacion': presentacion[0],
        'nombrePresentacion': presentacion[1],
        'cantidadBase': presentacion[2],
        'unidadMedida': presentacion[3]
    } for presentacion in presentaciones])


@app.route("/getProveedorPorPresentacion/<int:id_presentacion>")
def get_proveedor_por_presentacion(id_presentacion):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.idProveedor, 
            p.nombreProveedor, 
            ps.precioProveedor, 
            ps.idPresentacionFK
        FROM proveedoresinsumos ps
        JOIN proveedores p ON ps.idProveedorFK = p.idProveedor
        WHERE ps.idPresentacionFK = %s
    """, (id_presentacion,))
    proveedores = cur.fetchall()
    cur.close()
    return jsonify([{
        'idProveedor': proveedor[0],
        'nombreProveedor': proveedor[1],
        'precioProveedor': proveedor[2],
        'idPresentacionFK': proveedor[3]
    } for proveedor in proveedores])    


@app.route("/registrarCompraInsumos", methods=["POST"])
def registrarCompraInsumos():
    try:
        cur = mysql.connection.cursor()
        id_empleado = session.get("user")[5]  # Asegúrate de que "user" está en la sesión
        print("ID de empleado:", id_empleado)  # Verifica que el ID de empleado se obtiene correctamente
        id_proveedor = request.form.get("proveedor-select")
        insumos_data = []
        index = 0
        while f"insumos[{index}][idInsumo]" in request.form:
            print(f"Procesando el insumo en el índice {index}")  # Verifica que el índice cambia
            insumo = {
                "idInsumo": request.form.get(f"insumos[{index}][idInsumo]"),
                "idPresentacionFK": request.form.get(f"insumos[{index}][idPresentacionFK]"),
                "idProveedorFK": id_proveedor,
                "cantidadCompra": float(request.form.get(f"insumos[{index}][cantidadCompra]")),
                "fechaCaducidad": request.form.get(f"insumos[{index}][fechaCaducidad]"),
            }
            insumos_data.append(insumo)
            index += 1  # Asegúrate de que el índice se incremente
            print(insumos_data)  # Verifica que los datos se están acumulando correctamente
        if not insumos_data:
            flash("Error: Debe agregar al menos un insumo.", "danger")
            return redirect(url_for("insumos_inventory"))
        #El codigo se detiene aqui
        cur.execute("INSERT INTO compra (idProveedorFK, idEmpleadoFK, fechaCompra ) VALUES (%s, %s, NOW())", (id_proveedor, id_empleado))
        id_compra = cur.lastrowid
        if not id_compra:
            flash("Error al registrar la compra.", "danger")
            return redirect(url_for("insumos_inventory"))
        for insumo in insumos_data:
            print("Datos de insumo recibidos:", insumo)
            id_insumo = insumo["idInsumo"]
            id_presentacion = insumo["idPresentacionFK"]
            id_proveedor = insumo["idProveedorFK"]
            cantidad = insumo["cantidadCompra"]
            fecha_caducidad = insumo["fechaCaducidad"]
            # Obtener información adicional del insumo
            cur.execute("""
                SELECT 
                    p.cantidadBase, 
                    ps.precioProveedor
                FROM presentacionesinsumos p
                JOIN proveedoresinsumos ps ON p.idPresentacion = ps.idPresentacionFK
                WHERE p.idPresentacion = %s AND ps.idProveedorFK = %s
            """, (id_presentacion, id_proveedor))
            resultado = cur.fetchone()

            if resultado:
                cantidad_base = resultado[0]
                precio_unitario = resultado[1]
                # Calcular cantidad total en unidades base y precio total
                cantidad_total = cantidad * cantidad_base
                precio_total = precio_unitario * cantidad

                # Insertar en detallecompra
                cur.execute("""
                    INSERT INTO detallecompra (
                        idPedidoFK, 
                        idPresentacionFK, 
                        cantidad, 
                        precioCompra
                    ) VALUES (%s, %s, %s, %s)
                """, (id_compra, id_presentacion, cantidad, precio_total))

                # Insertar en inventarioInsumos
                cur.execute("""
                    INSERT INTO inventarioInsumos (
                        idInsumoFK, 
                        cantidad, 
                        fechaCaducidad
                    ) VALUES (%s, %s, %s)
                """, (id_insumo, cantidad_total, fecha_caducidad))

        # Confirmar la transacción
        mysql.connection.commit()
        flash("Compra registrada exitosamente con todos los insumos.", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al registrar la compra: {str(e)}", "danger")
        app.logger.error(f"Error en registrarCompraInsumos: {str(e)}")

    finally:
        cur.close()

    return redirect(url_for("insumos_inventory"))



@app.route("/registrarMermaInsumo", methods=["POST"])
def registrarMerma():
    if request.method == "POST":
        idInventarioInsumoFK = request.form["idInventarioInsumoFK"]
        tipoMerma = request.form["tipoMerma"]
        cantidad = int(request.form["cantidad"])
        observaciones = request.form["observaciones"]
        cantidadActual = int(round(float(request.form["cantidadActual"])))
        resta = cantidadActual - cantidad
        if resta < 0:
            flash("La cantidad de merma excede la cantidad disponible.", "danger")
            return redirect(url_for("insumos_inventory"))
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO mermas (tipoMerma, idInventarioInsumoFK, cantidad, fechaRegistro, observaciones) VALUES (%s, %s, %s, NOW(), %s)",
                (tipoMerma, idInventarioInsumoFK, cantidad, observaciones),
            )
            cur.execute(
                "UPDATE inventarioInsumos SET cantidad = %s WHERE idInventarioInsumo = %s;",
                (resta, idInventarioInsumoFK),
            )
            if resta == 0:
                cur.execute(
                    "UPDATE inventarioInsumos SET estadoLote = 'Vendido' WHERE idInventarioInsumo = %s",
                    (idInventarioInsumoFK,),
                )
                flash("Lote vacío", "success")
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            flash("Error al procesar la merma.", "danger")
        finally:
            cur.close()
        return redirect(url_for("insumos_inventory"))


@app.route("/registrarMermaLote", methods=["POST"])
def registrar_merma_lote():
    if request.method == "POST":
        id_lote = request.form["idLoteMerma"]
        cur = mysql.connection.cursor()
        try:
            # Obtener información del lote
            cur.execute("""
                SELECT idInventarioInsumo, idInsumoFK, cantidad 
                FROM inventarioInsumos 
                WHERE idInventarioInsumo = %s
            """, (id_lote,))
            lote = cur.fetchone()
            
            if not lote:
                flash("Lote no encontrado", "danger")
                return redirect(url_for("insumos_inventory"))
            
            id_inventario, id_insumo, cantidad = lote
            
            # Registrar merma del lote completo
            cur.execute("""
                INSERT INTO mermas (
                    tipoMerma, 
                    idInventarioInsumoFK, 
                    cantidad, 
                    fechaRegistro, 
                    observaciones
                ) VALUES (%s, %s, %s, NOW(), %s)
            """, ("Insumo caduco", id_inventario, cantidad, "Merma automática por caducidad del lote completo"))
            
            # Actualizar inventario (marcar como caducado y cantidad a 0)
            cur.execute("""
                UPDATE inventarioInsumos 
                SET cantidad = 0, 
                    estadoLote = 'Caducado' 
                WHERE idInventarioInsumo = %s
            """, (id_inventario,))
            
            mysql.connection.commit()
            flash("Merma del lote caducado registrada exitosamente", "success")
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al registrar merma del lote: {str(e)}", "danger")
            app.logger.error(f"Error en registrar_merma_lote: {str(e)}")
            
        finally:
            cur.close()
            
    return redirect(url_for("insumos_inventory"))