from flask import render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from db import app,mysql  

load_dotenv()


@app.route("/eliminarProveedor", methods=["POST"])
def eliminarProveedor():
    idProveedor = request.form["idProveedor"]
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.nombreInsumo 
        FROM insumos i
        INNER JOIN presentacionesinsumos pi ON i.idInsumo = pi.idInsumoFK
        INNER JOIN proveedoresinsumos pvi ON pi.idPresentacion = pvi.idPresentacionFK
        WHERE pvi.idProveedorFK = %s;
    """, (idProveedor,))
    insumos = cur.fetchall()
    if insumos:
        nombres_insumos = ", ".join(row[0] for row in insumos)
        flash(f"⚠️ Antes de eliminar este proveedor, cambia los siguientes insumos a otro proveedor: {nombres_insumos}", "warning")
        return redirect(url_for("registerProveedor"))
    cur.execute(
        "UPDATE proveedores SET estadoProveedor = 0 WHERE idProveedor = %s;",
        (idProveedor,)
    )
    mysql.connection.commit()
    cur.close()
    flash("✅Proveedor eliminado con éxito", "success")
    return redirect(url_for("registerProveedor"))


@app.route("/activarProveedor", methods=["POST", "GET"])
def activarProveedor():
    if request.method == "POST":
        idProveedor = request.form["idProveedor"]
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE proveedores SET estadoProveedor = 1 WHERE idProveedor = %s;",
            (idProveedor,),
        )
        mysql.connection.commit()
        cur.close()
        flash("Proveedor activado con éxito", "success")
        return redirect(url_for("registerProveedor"))
    proveedores = get_proveedores()
    return render_template("/production/Proveedores.html", proveedores=proveedores)


@app.route("/eliminarDefProveedor", methods=["POST", "GET"])
def deleteProveedor():
    if request.method == "POST":
        idProveedor = request.form["idProveedor"]
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM proveedores WHERE idProveedor = %s;",
            (idProveedor,),
        )
        mysql.connection.commit()
        cur.close()
        flash("Proveedor activado con éxito", "success")
        return redirect(url_for("registerProveedor"))


@app.route("/registerProveedor", methods=["POST", "GET"])
def registerProveedor():
    user = session.get("user")
    if not user or user[4] not in ["produccion", "administrador"]:
        return redirect(url_for("login"))
    if request.method == "POST":
        nombreProveedor = request.form["nombreProveedor"]
        contacto = request.form["contacto"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO proveedores (nombreProveedor, contacto, telefono, direccion) VALUES (%s, %s, %s, %s)",
            (nombreProveedor, contacto, telefono, direccion),
        )
        mysql.connection.commit()
        cur.close()
        flash("Proveedor registrado con éxito", "success")
        return redirect(url_for("registerProveedor"))
    proveedores=get_proveedores()
    print(proveedores)
    return render_template("/production/Proveedores.html",proveedores=proveedores, user=user)


@app.route("/modifyProveedor", methods=["POST", "GET"])
def modifyProveedor():
    if request.method == "POST":
        idProveedor = request.form.get("idProveedor") 
        print(idProveedor)
        nombreProveedor = request.form["Nombre"]
        contacto = request.form["Contacto"]
        telefono = request.form["Telefono"]
        direccion = request.form["Direccion"]
        if idProveedor:
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE proveedores SET nombreProveedor=%s, contacto=%s, telefono=%s, direccion=%s WHERE idProveedor=%s",
                (nombreProveedor, contacto, telefono, direccion, idProveedor),
            )
            mysql.connection.commit()
            cur.close()
            flash("Proveedor actualizado con éxito", "success")
        return redirect(url_for("registerProveedor"))
    proveedores = get_proveedores()
    return render_template("/production/Proveedores.html", proveedores=proveedores)


def get_proveedores(estado=1):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT idProveedor, nombreProveedor, contacto, telefono, direccion
        FROM proveedores
        WHERE estadoProveedor = %s
    """, (estado,))
    columnas = [col[0] for col in cur.description]
    proveedores = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
    cur.close()
    return proveedores


@app.route("/getProveedores", methods=["GET"])
def get_proveedores_json():
    if session.get("user") is None:
        return render_template("pages/error404.html"), 404
    user = session.get("user")
    if user[4] != "produccion":
        return render_template("pages/error404.html"), 404
    estado = request.args.get("estado", default=1, type=int)
    proveedores = get_proveedores(estado)
    return {"proveedores": proveedores}
