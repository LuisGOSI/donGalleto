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
            "idProveedorInsumo": insumo[7],
            "idProveedorFK": insumo[8],
            "precioProveedor": insumo[9],
        }
    else:
        return {"error": "Insumo no encontrado"}, 404


@app.route("/asignar_proveedor_presentacion", methods=["POST"])
def asignar_proveedor_presentacion():
    if request.method == "POST":
        idInsumo = request.form["idInsumo"]
        idProveedorFK = request.form["idProveedorFK"]
        precioProveedor = float(request.form["precioProveedor"])
        nombrePresentacion = request.form["nombrePresentacion"]
        cantidadBase = float(request.form["cantidadBase"])
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO presentacionesinsumos (idInsumoFK, nombrePresentacion, cantidadBase) VALUES (%s, %s, %s)",
            (idInsumo, nombrePresentacion, cantidadBase),
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


@app.route("/editarInsumo", methods=["POST"])
def editar_insumo():
    if request.method == "POST":
        idInsumo = request.form["idInsumoEditar"]
        nombreInsumo = request.form["nombreInsumoEditar"]
        unidadMedida = request.form["unidadMedidaEditar"]
        
        cur = mysql.connection.cursor()
        try:
            # Solo actualizamos los datos del insumo
            cur.execute(
                "UPDATE insumos SET nombreInsumo = %s, unidadMedida = %s WHERE idInsumo = %s",
                (nombreInsumo, unidadMedida, idInsumo),
            )
            mysql.connection.commit()
            print("Insumo actualizado correctamente.")
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar el insumo: {e}")
        finally:
            cur.close()
        
        return redirect(url_for("gestion_insumos"))


@app.route("/eliminarInsumo", methods=["POST"])
def eliminar_insumo():
    idInsumo = request.form["idInsumoEliminar"]
    cur = mysql.connection.cursor()
    
    try:
        # Eliminar las relaciones con proveedores
        cur.execute("""
            DELETE FROM proveedoresinsumos 
            WHERE idPresentacionFK IN (
                SELECT idPresentacion 
                FROM presentacionesinsumos 
                WHERE idInsumoFK = %s
            )
        """, (idInsumo,))
        
        # Eliminar las presentaciones del insumo
        cur.execute("DELETE FROM presentacionesinsumos WHERE idInsumoFK = %s", (idInsumo,))
        
        # Eliminar el insumo
        cur.execute("DELETE FROM insumos WHERE idInsumo = %s", (idInsumo,))
        
        mysql.connection.commit()
        print("Insumo y todo lo relacionado eliminado correctamente.")
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error al eliminar el insumo: {e}")
    finally:
        cur.close()
    
    return redirect(url_for("gestion_insumos"))

# Endpoint para obtener los datos de una presentación
@app.route("/get_presentacion/<int:idPresentacion>")
def get_presentacion(idPresentacion):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.idPresentacion,
            p.idInsumoFK,
            p.nombrePresentacion,
            p.cantidadBase,
            pi.idProveedorFK,
            pi.precioProveedor
        FROM 
            presentacionesinsumos p
        LEFT JOIN 
            proveedoresinsumos pi ON p.idPresentacion = pi.idPresentacionFK
        WHERE 
            p.idPresentacion = %s;
    """, (idPresentacion,))
    presentacion = cur.fetchone()
    cur.close()
    
    if presentacion:
        return {
            "idPresentacion": presentacion[0],
            "idInsumoFK": presentacion[1],
            "nombrePresentacion": presentacion[2],
            "cantidadBase": presentacion[3],
            "idProveedorFK": presentacion[4],
            "precioProveedor": presentacion[5],
        }
    else:
        return {"error": "Presentación no encontrada"}, 404

# Endpoint para editar presentación y proveedor
@app.route("/editarPresentacionProveedor", methods=["POST"])
def editar_presentacion_proveedor():
    if request.method == "POST":
        idPresentacion = request.form["idPresentacionEditar"]
        nombrePresentacion = request.form["nombrePresentacionEditar"]
        cantidadBase = request.form["cantidadBaseEditar"]
        idProveedorFK = request.form["proveedorEditar"]
        precioProveedor = request.form["precioProveedorEditar"]
        
        cur = mysql.connection.cursor()
        try:
            # Actualizar la presentación
            cur.execute(
                "UPDATE presentacionesinsumos SET nombrePresentacion = %s, cantidadBase = %s WHERE idPresentacion = %s",
                (nombrePresentacion, cantidadBase, idPresentacion),
            )
            # Actualizar el proveedor
            cur.execute(
                "UPDATE proveedoresinsumos SET idProveedorFK = %s, precioProveedor = %s WHERE idPresentacionFK = %s",
                (idProveedorFK, precioProveedor, idPresentacion),
            )
            mysql.connection.commit()
            print("Presentación y proveedor actualizados correctamente.")
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al actualizar la presentación y proveedor: {e}")
        finally:
            cur.close()
        
        return redirect(url_for("gestion_insumos"))

# Endpoint para eliminar presentación
@app.route("/eliminarPresentacion", methods=["POST"])
def eliminar_presentacion():
    if request.method == "POST":
        idPresentacion = request.form["idPresentacionEliminar"]
        cur = mysql.connection.cursor()
        try:
            # Eliminar la relación con el proveedor
            cur.execute("DELETE FROM proveedoresinsumos WHERE idPresentacionFK = %s", (idPresentacion,))
            # Eliminar la presentación
            cur.execute("DELETE FROM presentacionesinsumos WHERE idPresentacion = %s", (idPresentacion,))
            mysql.connection.commit()
            print("Presentación y relación con proveedor eliminados correctamente.")
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error al eliminar la presentación: {e}")
        finally:
            cur.close()
        
        return redirect(url_for("gestion_insumos"))
