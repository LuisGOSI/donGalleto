from flask import render_template, request, redirect, url_for, flash,jsonify, session
from dotenv import load_dotenv
from datetime import datetime
from db import app,mysql
from sessions import *  

load_dotenv()

@app.route("/getInveGalletas")   
def getInveGalletas():
    if session.get("user") is None:
        app.logger.error('Usuario desconocido intento acceder a inventario de galletas, acceso denegado')
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] != "produccion":
        app.logger.warning(f'El usuario con correo "{user[2]}" intento acceder a inventario de galletas, acceso denegado')
        return render_template("pages/error404.html"), 404
    hoy = datetime.today().date()
    lotesResumen = []
    cur = mysql.connection.cursor()
    cur.execute("SELECT idInvGalleta, nombreGalleta, fechaCaducidad, cantidad, estadoLote FROM dongalletodev.invgalletastabla where estadoLote = 'Disponible';")
    galletas_raw = cur.fetchall()
    for id_lote, nombre, fecha_caducidad, cantidad, estado in galletas_raw:
        if isinstance(fecha_caducidad, str):
            fecha_caducidad = datetime.strptime(fecha_caducidad, "%Y-%m-%d").date()
        dias_restantes = (fecha_caducidad - hoy).days
        if dias_restantes <= 0 and estado == "Disponible":
            cur.execute("""
                UPDATE inventarioGalletas
                SET estadoLote = 'Caducado' 
                WHERE idInvGalleta = %s
            """, (id_lote,))
            mysql.connection.commit()
            continue
        lotesResumen.append({
            "id_lote": id_lote,
            "nombre": nombre,
            "fecha_mas_proxima": fecha_caducidad.strftime("%d/%m/%Y"),
            "cantidad_proxima_caducar": cantidad,
            "dias_restantes": dias_restantes,
            "estado": estado
        })
    cur.close()
    galletasTabla = getGalletasTabla()
    galletasResumen = getGalletasResumen()
    app.logger.debug(f'rol verificado, el usuario con correo "{user[2] }" accedio correctamente a la vista inventario de galletas')
    return render_template("/production/InveGalletas.html", galletasTabla=galletasTabla, galletasResumen=galletasResumen, lotesResumen=lotesResumen, hoy=hoy, user=user)


@app.route("/registrarMermaGalleta", methods=["POST"])
def registrarMermaGalleta():
    user=session.get("user")
    if request.method == "POST":
        idInventarioGalletaFK = request.form["idInventarioGalletaFK"]
        tipoMerma = request.form["tipoMerma"]
        cantidad = int(request.form["cantidad"])
        observaciones = request.form["observaciones"]
        cantidadActual = int(request.form["cantidadActual"])
        resta = cantidadActual - cantidad
        if resta < 0:
            flash("La cantidad de merma excede la cantidad disponible.", "danger")
            return redirect(url_for("getInveGalletas"))
        if cantidad == 0:
            flash("la cantidad no puede ser 0", "danger")
            return redirect(url_for("getInveGalletas"))
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO mermas (tipoMerma, idInventarioGalletaFK, cantidad, fechaRegistro, observaciones) VALUES (%s, %s, %s, NOW(), %s)",
                (tipoMerma, idInventarioGalletaFK, cantidad, observaciones),
            )
            cur.execute(
                "UPDATE inventarioGalletas SET cantidadGalletas = %s WHERE idInvGalleta = %s;",
                (resta, idInventarioGalletaFK),
            )
            if resta == 0:
                cur.execute(
                    "UPDATE inventarioGalletas SET estadoLote = 'Vendido' WHERE idInvGalleta = %s",
                    (idInventarioGalletaFK,),
                )
                flash("Lote vacío", "success")
            mysql.connection.commit()
            app.logger.debug(f'el usuario con correo "{user[2] }" registro mermas en inventario de galletas en el lote No. "{idInventarioGalletaFK}"')
            flash("Merma Registrada", "success")
        except Exception as e:
            mysql.connection.rollback()
            app.logger.error(f'el usuario con correo "{user[2] }" tuvo problemas en registrar mermas en inventario de galletas en el lote No. "{idInventarioGalletaFK}"')
            flash("Error al procesar la merma.", "danger")
        finally:
            cur.close()
        return redirect(url_for("getInveGalletas"))
    return render_template("getInveGalletas")

        
def getGalletasTabla(estadoLote="Disponible"):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dongalletodev.invgalletastabla where estadoLote = %s and cantidad>1;", (estadoLote,))
    columnas = [col[0] for col in cur.description]
    galletas = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
    cur.close()
    return galletas

@app.route("/actualizar_tabla")
def actualizar_tabla():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] != "produccion":
        return render_template("pages/error404.html"), 404
    estado = request.args.get("estado", "Disponible")
    galletas = getGalletasTabla(estado)
    return jsonify(galletas)

def getGalletasResumen():
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombreGalleta, cantidad, fechaCaducidad FROM dongalletodev.invgalletastabla where estadoLote = 'Disponible';")
    resumen = {}
    for nombre, cantidad, fecha_cad in cur.fetchall():
        if nombre not in resumen:
            resumen[nombre] = {"cantidad_total": 0, "fecha_mas_proxima": None, "cantidad_proxima_caducar": 0}
        resumen[nombre]["cantidad_total"] += cantidad
        if resumen[nombre]["fecha_mas_proxima"] is None or fecha_cad < resumen[nombre]["fecha_mas_proxima"]:
            resumen[nombre]["fecha_mas_proxima"] = fecha_cad
            resumen[nombre]["cantidad_proxima_caducar"] = cantidad
        elif fecha_cad == resumen[nombre]["fecha_mas_proxima"]:
            resumen[nombre]["cantidad_proxima_caducar"] += cantidad
    cur.close()
    return resumen


@app.route("/enviarMerma", methods=["POST"])
def enviarMerma():
    user=session.get("user")
    if request.method == "POST":
        idInventarioGalletaFK = request.form["idInventarioGalletaFK"]
        tipoMerma = "Galletas caducas"
        observaciones = "No se vendieron antes de su fecha"
        cur = mysql.connection.cursor()
        cur.execute("SELECT cantidadGalletas FROM inventarioGalletas WHERE idInvGalleta = %s", (idInventarioGalletaFK,))
        cantidad = cur.fetchone()[0]
        try:
            cur.execute(
                "INSERT INTO mermas (tipoMerma, idInventarioGalletaFK, cantidad, fechaRegistro, observaciones) VALUES (%s, %s, %s, NOW(), %s)",
                (tipoMerma, idInventarioGalletaFK, cantidad, observaciones),
            )
            cur.execute(
                "UPDATE inventarioGalletas SET cantidadGalletas = 0 WHERE idInvGalleta = %s;",
                (idInventarioGalletaFK,),
            )
            app.logger.debug(f'el usuario con correo "{user[2] }" mando las galletas caducadas del lote No. "{idInventarioGalletaFK}" a merma')
            flash("Merma Registrada", "success")
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            app.logger.error(f'el usuario con correo "{user[2] }" tuvo problemas en mandar las galletas caducadas del lote No. "{idInventarioGalletaFK}" a merma')
            flash("Error al procesar la merma.", "danger")
        finally:
            cur.close()
        return redirect(url_for("getInveGalletas"))
    return render_template("getInveGalletas")
