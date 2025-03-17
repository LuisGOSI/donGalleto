from flask import render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

from db import app,mysql  

load_dotenv()


@app.route("/eliminarProveedor", methods=["POST", "GET"])
def eliminarProveedor():
    if request.method == "POST":
        idProveedor = request.form["idProveedor"]
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE proveedores SET estadoProveedor = 0 WHERE idProveedor = %s;",
            (idProveedor,),
        )
        mysql.connection.commit()
        cur.close()
        flash("Proveedor eliminado con éxito", "success")
        return redirect(url_for("registerProveedor"))
    proveedores = get_proveedores()
    return render_template("/production/Proveedores.html", proveedores=proveedores)


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
    return render_template("/production/Proveedores.html",proveedores=proveedores)


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
    estado = request.args.get("estado", default=1, type=int)
    proveedores = get_proveedores(estado)
    return {"proveedores": proveedores}
