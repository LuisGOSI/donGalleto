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
        return (
            jsonify({"error": "No se encontró el ID del empleado en la sesión."}),
            401,
        )
    productos = data.get("productos", [])
    subtotal = data.get("subtotal", 0)
    descuento = data.get("descuento", 0)
    total = data.get("total", 0)
    try:
        # Registrar la venta en la tabla 'ventas'
        cursor.execute(
            """
            INSERT INTO ventas (idEmpleadoFK, idClienteFK, fechaVenta, descuento) 
            VALUES (%s, NULL, %s, %s)
        """,
            (idEmpleado, datetime.now(), descuento),
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
            
            if tipo == "paquete 1kg":
                cantidad = cantidad * 6

            # Insertar en detalleventas
            cursor.execute(
                """
                INSERT INTO detalleventas (idVentaFK, idGalletaFK, cantidadVendida, tipoVenta, PrecioUnitarioVendido)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (idVenta, idGalleta, cantidad, tipo, precio),
            )

            # 3. Actualizar inventario de galletas
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
                (cantidad, idGalleta, cantidad),
            )

        mysql.connection.commit()
        
        
        # Generar PDF en lugar de enviar correo
        pdf_path = generar_pdf_ticket(idVenta, productos, subtotal, descuento, total)
        
        if pdf_path:
            # Obtener solo el nombre del archivo para la respuesta
            pdf_filename = os.path.basename(pdf_path)
            return jsonify({
                "mensaje": "Venta registrada con éxito",
                "pdf_ticket": pdf_filename,
                "pdf_url": f"/static/tickets/{pdf_filename}"
            }), 200
        else:
            return jsonify({
                "mensaje": "Venta registrada pero falló la generación del PDF",
                "pdf_ticket": None
            }), 200
            
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
