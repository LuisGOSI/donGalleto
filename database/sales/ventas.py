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
    print(idEmpleado)
    print(session.get("user"))
    if not idEmpleado:
        return (
            jsonify({"error": "No se encontró el ID del empleado en la sesión."}),
            401,
        )
    productos = data.get("productos", [])
    subtotal = data.get("subtotal", 0)
    descuento = data.get("descuento", 0)
    total = data.get("total", 0)
    tipo_venta = data.get("tipoVenta", "local")  # Nuevo campo: 'local' o 'online'

    try:
        # Registrar la venta en la tabla 'ventas'
        cursor.execute(
            """
            INSERT INTO ventas (idEmpleadoFK, idClienteFK, fechaVenta, descuento, tipoVenta, estadoVenta) 
            VALUES (%s, NULL, %s, %s, %s,
                    CASE WHEN %s = 'online' THEN 'pendiente' ELSE 'confirmada' END)
        """,
            (idEmpleado, datetime.now(), descuento, tipo_venta, tipo_venta),
        )

        idVenta = cursor.lastrowid
        # Registrar cada producto en 'detalleventas' y actualizar inventario
        for producto in productos:
            nombre = producto["name"]
            cantidad = producto["quantity"]
            tipo = producto["type"].lower()
            precio = producto["price"]

            # Obtener el ID de la galleta
            cursor.execute(
                "SELECT idGalleta FROM galletas WHERE nombreGalleta = %s", (nombre,)
            )
            galleta = cursor.fetchone()
            if not galleta:
                return jsonify({"error": f"Galleta '{nombre}' no encontrada"}), 400
            idGalleta = galleta[0]

            cantidadVendida = cantidad
            cantidad_galletas = 1  # Valor por defecto
            
            if tipo == "paquete 1kg":
                peso_galleta = revisar_gramaje_por_id(idGalleta)
                if isinstance(peso_galleta, dict) and "error" in peso_galleta:
                    return peso_galleta, 400
                cantidad_galletas = round(1000 / peso_galleta) * cantidad
                cantidadVendida = cantidad_galletas
            elif tipo == "paquete 700gr":
                peso_galleta = revisar_gramaje_por_id(idGalleta)
                if isinstance(peso_galleta, dict) and "error" in peso_galleta:
                    return peso_galleta, 400
                cantidad_galletas = round(700 / peso_galleta) * cantidad
                cantidadVendida = cantidad_galletas
            elif tipo == "gramaje":
                peso_galleta = revisar_gramaje_por_id(idGalleta)
                if isinstance(peso_galleta, dict) and "error" in peso_galleta:
                    return peso_galleta, 400
                cantidad_galletas = round(cantidad / peso_galleta)
                cantidadVendida = cantidad_galletas

            cursor.execute(
                """
                INSERT INTO detalleventas (idVentaFK, idGalletaFK, cantidadVendida, tipoVenta, PrecioUnitarioVendido, cantidad_galletas)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (idVenta, idGalleta, cantidad, tipo, precio, cantidad_galletas),
            )

            # 3. Actualizar inventario de galletas
            if tipo_venta == "local":
                cursor.execute(
                    """
                    UPDATE inventariogalletas 
                    SET cantidadGalletas = cantidadGalletas - %s
                    WHERE idProduccionFK = (
                        SELECT idProduccion 
                        FROM (
                            SELECT p.idProduccion 
                            FROM produccion p
                            INNER JOIN recetas r ON p.idRecetaFK = r.idReceta
                            INNER JOIN inventariogalletas ig ON p.idProduccion = ig.idProduccionFK
                            WHERE r.idGalletaFK = %s
                            AND ig.cantidadGalletas >= %s 
                            AND ig.estadoLote = 'Disponible'
                            ORDER BY ig.fechaCaducidad ASC  # Prioriza lotes próximos a caducar
                            LIMIT 1  # Selecciona el lote más antiguo con stock suficiente
                        ) AS subquery
                    )
                    """,
                    (cantidadVendida, idGalleta, cantidadVendida),
                )

        mysql.connection.commit()

        # Generar PDF en lugar de enviar correo
        pdf_path = generar_pdf_ticket(idVenta, productos, subtotal, descuento, total)

        if pdf_path:
            # Obtener solo el nombre del archivo para la respuesta
            pdf_filename = os.path.basename(pdf_path)
            return (
                jsonify(
                    {
                        "mensaje": "Venta registrada con éxito",
                        "pdf_ticket": pdf_filename,
                        "pdf_url": f"/static/tickets/{pdf_filename}",
                        "tipo_venta": tipo_venta,
                        "estado_venta": (
                            "pendiente" if tipo_venta == "online" else "confirmada"
                        ),
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "mensaje": "Venta registrada pero falló la generación del PDF",
                        "pdf_ticket": None,
                        "tipo_venta": tipo_venta,
                        "estado_venta": (
                            "pendiente" if tipo_venta == "online" else "confirmada"
                        ),
                    }
                ),
                200,
            )

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
        # Verificar que la venta existe y es online pendiente
        cursor.execute(
            "SELECT tipoVenta, estadoVenta FROM ventas WHERE idVenta = %s", (idVenta,)
        )
        venta = cursor.fetchone()

        if not venta:
            return jsonify({"error": "Venta no encontrada"}), 404

        tipo_venta, estado_venta = venta

        if tipo_venta != "online" or estado_venta != "pendiente":
            return (
                jsonify({"error": "Solo se pueden confirmar ventas online pendientes"}),
                400,
            )

        # Obtener los detalles de la venta para actualizar inventario
        cursor.execute(
            "SELECT idGalletaFK, cantidadVendida, tipoVenta FROM detalleventas WHERE idVentaFK = %s",
            (idVenta,),
        )
        detalles = cursor.fetchall()

        # Actualizar inventario para cada producto
        for detalle in detalles:
            idGalleta, cantidad, tipo = detalle

            cantidadVendida = cantidad
            if tipo == "paquete 1kg":
                peso_galleta = revisar_gramaje_por_id(idGalleta)
                if isinstance(peso_galleta, dict) and "error" in peso_galleta:
                    return peso_galleta, 400
                cantidadVendida = round(cantidad * 1000 / peso_galleta)
            elif tipo == "paquete 700gr":
                peso_galleta = revisar_gramaje_por_id(idGalleta)
                if isinstance(peso_galleta, dict) and "error" in peso_galleta:
                    return peso_galleta, 400
                cantidadVendida = round(cantidad * 700 / peso_galleta)

            cursor.execute(
                """
                UPDATE inventariogalletas 
                SET cantidadGalletas = cantidadGalletas - %s
                WHERE idProduccionFK = (SELECT idProduccion FROM produccion WHERE idRecetaFK = (SELECT idReceta FROM recetas WHERE idGalletaFK = %s) LIMIT 1)
                AND cantidadGalletas >= %s
                AND estadoLote = 'Disponible'
                ORDER BY fechaCaducidad ASC
                LIMIT 1
                """,
                (cantidadVendida, idGalleta, cantidadVendida),
            )

        # Actualizar estado de la venta a confirmada
        cursor.execute(
            "UPDATE ventas SET estadoVenta = 'confirmada' WHERE idVenta = %s",
            (idVenta,),
        )

        mysql.connection.commit()
        return jsonify({"mensaje": "Venta confirmada e inventario actualizado"}), 200

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
        print(venta)
        if not venta:
            return jsonify({"error": "Venta no encontrada"}), 404
        cursor.execute(
            """
            SELECT dv.idDetalleVenta, dv.idVentaFK, dv.idGalletaFK, dv.cantidadVendida,
            dv.tipoVenta, dv.PrecioUnitarioVendido, g.nombreGalleta
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
        total_venta = sum(detalle[5] * detalle[3] for detalle in detalles)

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
