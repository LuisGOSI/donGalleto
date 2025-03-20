from flask import request, redirect, url_for
from db import app,mysql  
from dotenv import load_dotenv

load_dotenv()

# Registar un insumo
@app.route("/register_insumos", methods=["POST"])
def register_insumo():
    if request.method == "POST":
        nombreInsumo = request.form["nombreInsumo"]
        unidadMedida = request.form["unidadMedida"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO insumos (nombreInsumo, unidadMedida, cantidadInsumo) VALUES (%s, %s, %s)",
            (nombreInsumo, unidadMedida, 0),  # cantidadInsumo = 0 por default :v - podemos eliminarlo de la bd pq es un campo calculado
        )
        mysql.connection.commit()
        cur.close()
        print("Insumo registrado")
        return redirect(url_for("gestion_insumos"))

# Ruta para obtener los insumos
@app.route("/get_insumo/<int:idInsumo>")
def get_insumo(idInsumo):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            i.idInsumo,
            i.nombreInsumo,
            i.unidadMedida,
            i.cantidadInsumo,
            p.idPresentacion,
            p.nombrePresentacion,
            p.cantidadBase,
            p.unidadBase,
            pr.idProveedorInsumo,
            pr.idProveedorFK,
            pr.precioProveedor
        FROM 
            insumos i
        LEFT JOIN 
            presentacionesinsumos p ON i.idInsumo = p.idInsumoFK
        LEFT JOIN 
            proveedoresinsumos pr ON p.idPresentacion = pr.idPresentacionFK
        WHERE 
            i.idInsumo = %s;
    """, (idInsumo,))
    insumo = cur.fetchone()
    cur.close()
    if insumo:
        return {
            "idInsumo": insumo[0],
            "nombreInsumo": insumo[1],
            "unidadMedida": insumo[2],
            "cantidadInsumo": insumo[3],
            "idPresentacion": insumo[4],
            "nombrePresentacion": insumo[5],
            "cantidadBase": insumo[6],
            "unidadBase": insumo[7],
            "idProveedorInsumo": insumo[8],
            "idProveedorFK": insumo[9],
            "precioProveedor": insumo[10],
        }
    else:
        return {"error": "Insumo no encontrado"}, 404


# Ruta para asignar presentacion de un proveedor a un insumo
@app.route("/asignar_proveedor_presentacion", methods=["POST"])
def asignar_proveedor_presentacion():
    if request.method == "POST":
        idInsumo = request.form["idInsumo"]
        idProveedorFK = request.form["idProveedorFK"]
        precioProveedor = float(request.form["precioProveedor"])
        nombrePresentacion = request.form["nombrePresentacion"]
        cantidadBase = float(request.form["cantidadBase"])
        unidadBase = request.form["unidadMedidaAsignar"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO presentacionesinsumos (idInsumoFK, nombrePresentacion, cantidadBase, unidadBase) VALUES (%s, %s, %s, %s)",
            (idInsumo, nombrePresentacion, cantidadBase, unidadBase),
        )
        idPresentacion = cur.lastrowid
        cur.execute(
            "INSERT INTO proveedoresinsumos (idProveedorFK, idPresentacionFK, precioProveedor) VALUES (%s, %s, %s)",
            (idProveedorFK, idPresentacion, precioProveedor),
        )
        mysql.connection.commit()
        cur.close()
        print("Prov y presentacion asignados")
        return redirect(url_for("gestion_insumos"))


# Ruta para editar un insumo
@app.route("/editarInsumo", methods=["POST"])
def editar_insumo():
    if request.method == "POST":
        idInsumo = request.form["idInsumoEditar"]
        nombreInsumo = request.form["nombreInsumoEditar"]
        unidadMedida = request.form["unidadMedidaEditar"]
        idPresentacion = request.form["idPresentacionEditar"]
        nombrePresentacion = request.form["presentacionEditar"]
        cantidad = request.form["cantidadEditar"]
        cantidadBase = request.form["cantidadBaseEditar"]
        idProveedorInsumo = request.form["idProveedorInsumoEditar"]
        idProveedorFK = request.form["proveedorEditar"]
        precioProveedor = request.form["precioEditar"]
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "UPDATE insumos SET nombreInsumo = %s, unidadMedida = %s, cantidadInsumo = %s WHERE idInsumo = %s",
                (nombreInsumo, unidadMedida, cantidad, idInsumo),
            )
            cur.execute(
                "UPDATE presentacionesinsumos SET nombrePresentacion = %s, cantidadBase = %s WHERE idPresentacion = %s",
                (nombrePresentacion, cantidadBase, idPresentacion),
            )
            cur.execute(
                "UPDATE proveedoresinsumos SET idProveedorFK = %s, precioProveedor = %s WHERE idProveedorInsumo = %s",
                (idProveedorFK, precioProveedor, idProveedorInsumo),
            )
            mysql.connection.commit()
            print("Insumo, presentación y proveedor actualizados correctamente.")
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar el insumo: {e}")
        finally:
            cur.close()
        return redirect(url_for("gestion_insumos"))


# Ruta para eliminar un insumo
@app.route("/eliminarInsumo", methods=["POST"])
def eliminar_insumo():
    idInsumo = request.form["idInsumoEliminar"]
    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM proveedoresinsumos WHERE idPresentacionFK IN (SELECT idPresentacion FROM presentacionesinsumos WHERE idInsumoFK = %s)""", (idInsumo,))
    cur.execute("DELETE FROM presentacionesinsumos WHERE idInsumoFK = %s", (idInsumo,))
    cur.execute("DELETE FROM insumos WHERE idInsumo = %s", (idInsumo,))
    mysql.connection.commit()
    cur.close()
    print("Insumo eliminado")
    return redirect(url_for("gestion_insumos"))