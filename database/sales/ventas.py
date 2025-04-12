from db import app, mysql
from pdf_ticket import generar_pdf_ticket
from flask import jsonify, request, session, jsonify
from datetime import datetime
import os


@app.route("/registrarVenta", methods=["POST"])
def registrar_venta():
    cursor = mysql.connection.cursor()
    data = request.get_json()
    idEmpleado = session.get("user")[5]
    if not idEmpleado:
        return jsonify({"error": "No se encontró el ID del empleado en la sesión."}), 401
    
    productos = data.get("productos", [])
    subtotal = 0
    productos_para_pdf = []
    
    try:
        # Registrar la venta en la tabla 'ventas'
        cursor.execute(
            """
            INSERT INTO ventas (idEmpleadoFK, idClienteFK, fechaVenta, descuento, tipoVenta, estadoVenta) 
            VALUES (%s, NULL, %s, %s, %s,
                    CASE WHEN %s = 'online' THEN 'pendiente' ELSE 'confirmada' END)
            """,
            (idEmpleado, datetime.now(), data.get("descuento", 0), data.get("tipoVenta", "local"), data.get("tipoVenta", "local")),
        )

        idVenta = cursor.lastrowid
        
        for producto in productos:
            nombre = producto["name"]
            cantidad = producto["quantity"]
            tipo = producto["type"].lower()
            precio_base = producto.get("basePrice", producto["price"])
            
            # Obtener el ID de la galleta
            cursor.execute(
                "SELECT idGalleta, gramaje FROM galletas WHERE nombreGalleta = %s", (nombre,)
            )
            galleta = cursor.fetchone()
            if not galleta:
                return jsonify({"error": f"Galleta '{nombre}' no encontrada"}), 400
                
            idGalleta, peso_galleta = galleta
            
            # Preparar datos para PDF y DB
            precio_unitario = precio_base
            cantidad_galletas = cantidad
            cantidad_vendida = cantidad
            
            if tipo == "paquete 1kg":
                cantidad_galletas = round(1000 / peso_galleta)
                precio_unitario = (cantidad_galletas * precio_base) * 0.93
                cantidad_vendida = cantidad_galletas * cantidad
            elif tipo == "paquete 700gr":
                cantidad_galletas = round(700 / peso_galleta)
                precio_unitario = (cantidad_galletas * precio_base) * 0.93
                cantidad_vendida = cantidad_galletas * cantidad
            elif tipo == "gramaje":
                cantidad_galletas = round(cantidad / peso_galleta)
                precio_unitario = precio_base
                cantidad_vendida = cantidad_galletas
            
            productos_para_pdf.append({
                "name": nombre,
                "quantity": cantidad,
                "type": producto["type"],
                "price": precio_unitario if tipo != "gramaje" else precio_base,
                "subtotal": precio_unitario * cantidad if tipo != "gramaje" else precio_base * cantidad_galletas
            })
            
            subtotal += productos_para_pdf[-1]["subtotal"]
            
            # Insertar en detalleventas
            cursor.execute(
                """
                INSERT INTO detalleventas (idVentaFK, idGalletaFK, cantidadVendida, tipoVenta, PrecioUnitarioVendido, cantidad_galletas)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (idVenta, idGalleta, cantidad, tipo, precio_unitario, cantidad_vendida),
            )

            # Actualizar inventario - Lógica mejorada
            if data.get("tipoVenta", "local") == "local":
                cantidad_restante = cantidad_vendida
                
                # Obtenemos lotes ordenados por fecha de caducidad (más cercana primero)
                cursor.execute(
                    """
                    SELECT ig.idInvGalleta, ig.cantidadGalletas
                    FROM inventariogalletas ig
                    INNER JOIN produccion p ON ig.idProduccionFK = p.idProduccion
                    INNER JOIN recetas r ON p.idRecetaFK = r.idReceta
                    WHERE r.idGalletaFK = %s
                    AND ig.estadoLote = 'Disponible'
                    AND ig.cantidadGalletas > 0
                    ORDER BY ig.fechaCaducidad ASC
                    """,
                    (idGalleta,)
                )
                lotes_disponibles = cursor.fetchall()
                
                if not lotes_disponibles:
                    return jsonify({"error": f"No hay stock disponible para la galleta '{nombre}'"}), 400
                
                for lote in lotes_disponibles:
                    id_lote, stock_lote = lote
                    cantidad_a_descontar = min(stock_lote, cantidad_restante)
                    
                    # Actualizar el lote
                    nuevo_stock = stock_lote - cantidad_a_descontar
                    estado_lote = 'Vendido' if nuevo_stock == 0 else 'Disponible'
                    
                    cursor.execute(
                        """
                        UPDATE inventariogalletas 
                        SET cantidadGalletas = %s, estadoLote = %s
                        WHERE idInvGalleta = %s
                        """,
                        (nuevo_stock, estado_lote, id_lote)
                    )
                    
                    cantidad_restante -= cantidad_a_descontar
                    if cantidad_restante == 0:
                        break
                
                if cantidad_restante > 0:
                    return jsonify({"error": f"No hay suficiente stock para la galleta '{nombre}'. Faltan {cantidad_restante} unidades"}), 400

        mysql.connection.commit()
        
        # Recalcular total con el subtotal correcto
        descuento = data.get("descuento", 0)
        descuento_aplicado = (subtotal * descuento) / 100
        total = subtotal - descuento_aplicado
        
        # Generar PDF con los datos corregidos
        pdf_path = generar_pdf_ticket(idVenta, productos_para_pdf, subtotal, descuento, total)

        if pdf_path:
            pdf_filename = os.path.basename(pdf_path)
            return jsonify({
                "mensaje": "Venta registrada con éxito",
                "pdf_ticket": pdf_filename,
                "pdf_url": f"/static/tickets/{pdf_filename}",
                "tipo_venta": data.get("tipoVenta", "local"),
                "estado_venta": "pendiente" if data.get("tipoVenta", "local") == "online" else "confirmada",
            }), 200
        else:
            return jsonify({
                "mensaje": "Venta registrada pero falló la generación del PDF",
                "pdf_ticket": None,
                "tipo_venta": data.get("tipoVenta", "local"),
                "estado_venta": "pendiente" if data.get("tipoVenta", "local") == "online" else "confirmada",
            }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@app.route("/revisarGramajePorNombre1kg", methods=["POST"])
def revisar_gramaje_por_nombre_1kg():
    cursor = mysql.connection.cursor()
    data = request.get_json()
    nombreGalleta = data.get("name")
    try:
        if not nombreGalleta:
            return (jsonify({"error": "Falta el nombre de la  galleta"}),)

        # Obtener el peso de una galleta por su ID
        cursor.execute(
            "SELECT gramaje FROM galletas WHERE nombreGalleta = %s", (nombreGalleta,)
        )
        galleta = cursor.fetchone()
        if not galleta:
            return jsonify({"error": "Galleta no encontrada"}), 404

        peso_galleta = galleta[0]

        if peso_galleta <= 0:
            return jsonify({"error": "El peso de la galleta no es válido"}), 400

        # Calcular la cantidad de galletas necesarias para aproximarse a 1kg
        cantidad_galletas = round(1000 / peso_galleta)

        return (
            jsonify(
                {"pesoGalleta": peso_galleta, "cantidadPara1kg": cantidad_galletas}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@app.route("/revisarGramajePorNombre700gr", methods=["POST"])
def revisar_gramaje_por_nombre_700gr():
    cursor = mysql.connection.cursor()
    data = request.get_json()
    nombreGalleta = data.get("name")
    try:
        if not nombreGalleta:
            return (jsonify({"error": "Falta el nombre de la  galleta"}),)

        # Obtener el peso de una galleta por su ID
        cursor.execute(
            "SELECT gramaje FROM galletas WHERE nombreGalleta = %s", (nombreGalleta,)
        )
        galleta = cursor.fetchone()
        if not galleta:
            return jsonify({"error": "Galleta no encontrada"}), 404

        peso_galleta = galleta[0]

        if peso_galleta <= 0:
            return jsonify({"error": "El peso de la galleta no es válido"}), 400

        # Calcular la cantidad de galletas necesarias para aproximarse a 700gr
        cantidad_galletas = round(700 / peso_galleta)

        return (
            jsonify(
                {"pesoGalleta": peso_galleta, "cantidadPara700gr": cantidad_galletas}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@app.route("/revisarGramajePorNombre", methods=["POST"])
def revisar_gramaje_por_nombre():
    cursor = mysql.connection.cursor()
    data = request.get_json()
    nombreGalleta = data.get("name")
    try:
        if not nombreGalleta:
            return (jsonify({"error": "Falta el nombre de la galleta"}), 400)

        cursor.execute(
            "SELECT gramaje FROM galletas WHERE nombreGalleta = %s", (nombreGalleta,)
        )
        galleta = cursor.fetchone()
        if not galleta:
            return jsonify({"error": "Galleta no encontrada"}), 404

        peso_galleta = galleta[0]

        if peso_galleta <= 0:
            return jsonify({"error": "El peso de la galleta no es válido"}), 400

        return jsonify({"pesoGalleta": peso_galleta}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@app.route("/confirmarVentaOnline/<int:idVenta>", methods=["POST"])
def confirmar_venta_online(idVenta):
    cursor = mysql.connection.cursor()

    try:
        # 1. Validar que la venta existe y es online pendiente
        cursor.execute(
            "SELECT tipoVenta, estadoVenta FROM ventas WHERE idVenta = %s", 
            (idVenta,)
        )
        venta = cursor.fetchone()

        if not venta:
            return jsonify({"error": "Venta no encontrada"}), 404

        tipo_venta, estado_venta = venta

        if tipo_venta != "online" or estado_venta != "pendiente":
            return jsonify({
                "error": "Solo se pueden confirmar ventas online pendientes"
            }), 400

        # 2. Obtener los detalles de la venta (solo necesitamos cantidad_galletas)
        cursor.execute("""
            SELECT 
                dv.idGalletaFK,
                dv.cantidad_galletas,
                g.nombreGalleta
            FROM detalleventas dv
            JOIN galletas g ON dv.idGalletaFK = g.idGalleta
            WHERE dv.idVentaFK = %s
        """, (idVenta,))
        detalles = cursor.fetchall()

        # 3. Procesar cada item del detalle
        for detalle in detalles:
            id_galleta, cantidad_galletas, nombre_galleta = detalle

            # 4. Buscar lotes disponibles (más antiguos primero)
            cursor.execute("""
                SELECT 
                    ig.idInvGalleta,
                    ig.cantidadGalletas
                FROM inventariogalletas ig
                JOIN produccion p ON ig.idProduccionFK = p.idProduccion
                JOIN recetas r ON p.idRecetaFK = r.idReceta
                WHERE r.idGalletaFK = %s
                AND ig.estadoLote = 'Disponible'
                AND ig.cantidadGalletas > 0
                ORDER BY ig.fechaCaducidad ASC
            """, (id_galleta,))
            
            lotes = cursor.fetchall()
            galletas_por_descontar = cantidad_galletas

            # 5. Descontar de los lotes más antiguos primero
            for lote in lotes:
                id_lote, cant_disponible = lote
                
                if galletas_por_descontar <= 0:
                    break

                a_descontar = min(cant_disponible, galletas_por_descontar)

                # Actualizar el lote
                cursor.execute("""
                    UPDATE inventariogalletas
                    SET cantidadGalletas = cantidadGalletas - %s
                    WHERE idInvGalleta = %s
                """, (a_descontar, id_lote))

                # Actualizar estado si se agota
                if cant_disponible - a_descontar <= 0:
                    cursor.execute("""
                        UPDATE inventariogalletas
                        SET estadoLote = 'Vendido'
                        WHERE idInvGalleta = %s
                    """, (id_lote,))

                galletas_por_descontar -= a_descontar

            # Verificar si se pudo descontar todo
            if galletas_por_descontar > 0:
                raise Exception(
                    f"Stock insuficiente para {nombre_galleta}. "
                    f"Faltan {galletas_por_descontar} galletas en inventario"
                )

        # 6. Confirmar la venta
        cursor.execute("""
            UPDATE ventas
            SET estadoVenta = 'confirmada'
            WHERE idVenta = %s
        """, (idVenta,))

        mysql.connection.commit()
        return jsonify({
            "mensaje": "Venta confirmada e inventario actualizado correctamente",
            "detalle": "Se descontaron las galletas del inventario sin modificar recetas"
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@app.route("/cancelarVentaOnline/<int:idVenta>", methods=["POST"])
def cancelar_venta_online(idVenta):
    cursor = mysql.connection.cursor()

    try:
        # Verificar que la venta existe y es online pendiente
        cursor.execute("SELECT estadoVenta FROM ventas WHERE idVenta = %s", (idVenta,))
        venta = cursor.fetchone()

        if not venta:
            return jsonify({"error": "Venta no encontrada"}), 404

        estado_venta = venta[0]

        if estado_venta != "pendiente":
            return jsonify({"error": "Solo se pueden cancelar ventas pendientes"}), 400

        # Actualizar estado de la venta a cancelada
        cursor.execute(
            "UPDATE ventas SET estadoVenta = 'cancelada' WHERE idVenta = %s", (idVenta,)
        )
        
        #Borrar los detalles de la venta
        cursor.execute(
            "DELETE FROM detalleventas WHERE idVentaFK = %s", (idVenta,)
        )

        mysql.connection.commit()
        return jsonify({"mensaje": "Venta cancelada"}), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@app.route("/obtenerVentaOnline/<int:idVenta>", methods=["GET"])
def obtener_venta_online(idVenta):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT * FROM ventas WHERE idVenta = %s", (idVenta,))
        venta = cursor.fetchone()
        if not venta:
            return jsonify({"error": "Venta no encontrada"}), 404
        cursor.execute(
            """
            SELECT dv.idDetalleVenta, dv.idVentaFK, dv.idGalletaFK, dv.cantidadVendida,
            dv.tipoVenta, dv.PrecioUnitarioVendido, g.nombreGalleta, dv.cantidad_galletas
            FROM detalleventas dv
            JOIN galletas g ON dv.idGalletaFK = g.idGalleta
            WHERE dv.idVentaFK = %s
            """,
            (idVenta,),
        )
        detalles = cursor.fetchall()
        if not detalles:
            return jsonify({"error": "No se encontraron detalles para esta venta"}), 404

        # Calcular el total de la venta sumando los precios unitarios
        total_venta = sum(
            detalle[5] * (detalle[3] if detalle[4] in ["paquete 1kg", "paquete 700gr"] else detalle[7])
            for detalle in detalles
        )

        detalles_formateados = [
            {
                "idDetalleVenta": detalle[0],
                "idVentaFK": detalle[1],
                "idGalletaFK": detalle[2],
                "cantidadVendida": detalle[3],
                "tipoVenta": detalle[4],
                "precioUnitarioVendido": detalle[5],
                "nombre": detalle[6],
            }
            for detalle in detalles
        ]
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
    return (
        jsonify(
            {
                "venta": {
                    "idVenta": venta[0],
                    "idEmpleadoFK": venta[1],
                    "idClienteFK": None,
                    "fechaVenta": venta[3].strftime("%Y-%m-%d %H:%M:%S"),
                    "descuento": venta[4],
                    "tipoVenta": venta[5],
                    "estadoVenta": venta[6],
                    "totalVenta": total_venta,
                },
                "detalles": detalles_formateados,
            }
        ),
        200,
    )


def revisar_gramaje_por_id(idGalleta):
    cursor = mysql.connection.cursor()
    try:
        # Obtener el peso de una galleta por su ID
        cursor.execute(
            "SELECT gramaje FROM galletas WHERE idGalleta = %s", (idGalleta,)
        )
        galleta = cursor.fetchone()
        if not galleta:
            return jsonify({"error": "Galleta no encontrada"})

        peso_galleta = galleta[0]

        if peso_galleta <= 0:
            return jsonify({"error": "El peso de la galleta no es válido"})

        return peso_galleta

    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        cursor.close()

@app.route("/verificarStockVenta", methods=["POST"])
def verificar_stock_venta():
    cursor = mysql.connection.cursor()
    data = request.get_json()
    productos = data.get("productos", [])
    
    try:
        productos_sin_stock = []
        
        for producto in productos:
            nombre = producto["name"]
            cantidad = producto["quantity"]
            tipo = producto["type"].lower()
            
            # Obtener información de la galleta
            cursor.execute(
                "SELECT idGalleta, gramaje FROM galletas WHERE nombreGalleta = %s", (nombre,)
            )
            galleta = cursor.fetchone()
            if not galleta:
                return jsonify({"error": f"Galleta '{nombre}' no encontrada"}), 400
                
            idGalleta, peso_galleta = galleta
            
            # Calcular cantidad de galletas necesarias según el tipo
            if tipo == "paquete 1kg":
                cantidad_galletas = round(1000 / peso_galleta)
                cantidad_vendida = cantidad_galletas * cantidad
            elif tipo == "paquete 700gr":
                cantidad_galletas = round(700 / peso_galleta)
                cantidad_vendida = cantidad_galletas * cantidad
            elif tipo == "gramaje":
                cantidad_galletas = round(cantidad / peso_galleta)
                cantidad_vendida = cantidad_galletas
            else:  # unidad
                cantidad_vendida = cantidad
            
            # Verificar stock disponible
            cursor.execute(
                """
                SELECT SUM(ig.cantidadGalletas) as stock_total
                FROM inventariogalletas ig
                INNER JOIN produccion p ON ig.idProduccionFK = p.idProduccion
                INNER JOIN recetas r ON p.idRecetaFK = r.idReceta
                WHERE r.idGalletaFK = %s AND ig.estadoLote = 'Disponible'
                """,
                (idGalleta,)
            )
            stock = cursor.fetchone()[0] or 0
            
            if stock < cantidad_vendida:
                productos_sin_stock.append({
                    "nombre": nombre,
                    "stock_disponible": stock,
                    "stock_requerido": cantidad_vendida
                })
        
        if productos_sin_stock:
            return jsonify({
                "stock_suficiente": False,
                "productos_sin_stock": productos_sin_stock
            }), 200
        else:
            return jsonify({
                "stock_suficiente": True
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
    