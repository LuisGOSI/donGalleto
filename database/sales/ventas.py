import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db import app, mysql
from flask import jsonify, request, session, jsonify
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


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
        return jsonify({"mensaje": "Venta registrada con éxito"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            enviar_ticket(idVenta, productos, subtotal, descuento, total)
        except Exception as email_error:
            print(f"Error al enviar el correo: {email_error}")
        cursor.close()


def enviar_ticket(idVenta, productos, subtotal, descuento, total):
    try:
        # Crear el mensaje del correo
        mensaje = MIMEMultipart()
        mensaje["From"] = "ventasdongalleto@gmail.com"
        mensaje["To"] = "ventasdongalleto@gmail.com"
        mensaje["Subject"] = f"Ticket de Venta - ID: {idVenta}"

        # Formato del cuerpo del correo
        cuerpo = f"""
        
        Detalles de la venta:
        ID Venta: {idVenta}
        Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Productos comprados:
        """

        for producto in productos:
            cuerpo += f"{producto['name']} - {producto['quantity']} {producto['type']} - Precio: {producto['price']} C/U\n"

        cuerpo += f"""
        Subtotal: {subtotal} 
        Descuento: {descuento}
        Total: {total}

        """

        mensaje.attach(MIMEText(cuerpo, "plain"))

        # Enviar el correo
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("ventasdongalleto@gmail.com", os.getenv("MAIL_PASSWORD"))
            server.sendmail(mensaje["From"], mensaje["To"], mensaje.as_string())

        print("Correo enviado con el ticket de la compra.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
