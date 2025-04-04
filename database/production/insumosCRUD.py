from flask import request, redirect, url_for, flash
from db import app,mysql  
from dotenv import load_dotenv

load_dotenv()

@app.route("/register_insumos", methods=["POST"])
def register_insumo():
    if request.method == "POST":
        nombreInsumo = request.form["nombreInsumo"]
        unidadMedida = request.form["unidadMedida"]
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO insumos (nombreInsumo, unidadMedida, cantidadInsumo) VALUES (%s, %s, %s)",
                (nombreInsumo, unidadMedida, 0),  # cantidadInsumo = 0 por default :v - podemos eliminarlo de la bd pq es un campo calculado
            )
            mysql.connection.commit()
            flash("Insumo registrado exitosamente", "insumo_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al registrar insumo", "insumo_error")
        finally:
            cur.close()
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
        try:
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
            flash("Presentación y proveedor asignados correctamente", "presentacion_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al asignar presentación y proveedor", "presentacion_error")
        finally:
            cur.close()
        return redirect(url_for("gestion_insumos"))


@app.route("/editarInsumo", methods=["POST"])
def editar_insumo():
    if request.method == "POST":
        idInsumo = request.form["idInsumoEditar"]
        nombreInsumo = request.form["nombreInsumoEditar"]
        unidadMedida = request.form["unidadMedidaEditar"]
        
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "UPDATE insumos SET nombreInsumo = %s, unidadMedida = %s WHERE idInsumo = %s",
                (nombreInsumo, unidadMedida, idInsumo),
            )
            mysql.connection.commit()
            flash("Insumo actualizado correctamente", "insumo_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al actualizar insumo", "insumo_error")
        finally:
            cur.close()
        return redirect(url_for("gestion_insumos"))

@app.route("/eliminarInsumo", methods=["POST"])
def eliminar_insumo():
    idInsumo = request.form["idInsumoEliminar"]
    cur = mysql.connection.cursor()
    
    try:
        #obtener formatos vinculados
        cur.execute("""
            SELECT idFormatoFK FROM insumoFormatos 
            WHERE idInsumoFK = %s
        """, (idInsumo,))
        formatos_vinculados = [row[0] for row in cur.fetchall()]
        
        # Eliminar las relaciones en insumoFormatos
        cur.execute("""
            DELETE FROM insumoFormatos 
            WHERE idInsumoFK = %s
        """, (idInsumo,))
        
        # Eliminar los formatos de receta vinvulados al insumo
        for idFormato in formatos_vinculados:
            cur.execute("""
                DELETE FROM formatosRecetas 
                WHERE idFormato = %s AND NOT EXISTS (
                    SELECT 1 FROM insumoFormatos 
                    WHERE idFormatoFK = %s
                )
            """, (idFormato, idFormato))
        
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
        cur.execute("""
            DELETE FROM presentacionesinsumos 
            WHERE idInsumoFK = %s
        """, (idInsumo,))
        
        # Borrar el insumo
        cur.execute("""
            DELETE FROM insumos 
            WHERE idInsumo = %s
        """, (idInsumo,))
        
        mysql.connection.commit()
        flash("Insumo y todos sus datos relacionados eliminados correctamente", "insumo_success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al eliminar insumo", "insumo_error")
    finally:
        cur.close()
    return redirect(url_for("gestion_insumos"))

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
            flash("Presentación y proveedor actualizados correctamente", "presentacion_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al actualizar presentación y proveedor", "presentacion_error")
        finally:
            cur.close()
        return redirect(url_for("gestion_insumos"))

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
            flash("Presentación eliminada correctamente", "presentacion_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al eliminar presentación", "presentacion_error")
        finally:
            cur.close()
        return redirect(url_for("gestion_insumos"))
    
@app.route("/registrar_formato_receta", methods=["POST"])
def registrar_formato_receta():
    if request.method == "POST":
        idInsumo = request.form["idInsumoFormato"]
        nombreFormato = request.form["nombreFormato"]
        cantidadConvertida = float(request.form["cantidadConvertida"])
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO formatosRecetas (nombreFormato) VALUES (%s)",
                (nombreFormato,)
            )
            idFormato = cur.lastrowid
            
            cur.execute(
                "INSERT INTO insumoFormatos (idInsumoFK, idFormatoFK, cantidadConvertida) VALUES (%s, %s, %s)",
                (idInsumo, idFormato, cantidadConvertida)
            )
            
            mysql.connection.commit()
            flash("Formato de receta registrado exitosamente", "formato_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al registrar formato de receta", "formato_error")
        finally:
            cur.close()
            
        return redirect(url_for("gestion_insumos"))
    
@app.route("/obtener_formato_receta/<int:id_formato>")
def obtener_formato_receta(id_formato):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT fr.idFormato, fr.nombreFormato, i.unidadMedida, ifr.cantidadConvertida, i.idInsumo
        FROM formatosRecetas fr
        JOIN insumoFormatos ifr ON fr.idFormato = ifr.idFormatoFK
        JOIN insumos i ON ifr.idInsumoFK = i.idInsumo
        WHERE fr.idFormato = %s
    """, (id_formato,))
    formato = cur.fetchone()
    cur.close()
    
    if formato:
        return {
            'idFormato': formato[0],
            'nombreFormato': formato[1],
            'unidadBase': formato[2],
            'cantidadConvertida': float(formato[3]),
            'idInsumo': formato[4]
        }
    else:
        return {'error': 'Formato no encontrado'}, 404

@app.route("/editarFormatoReceta", methods=["POST"])
def editar_formato_receta():
    if request.method == "POST":
        id_formato = request.form["idFormatoEditar"]
        nombre_formato = request.form["nombreFormatoEditar"]
        cantidad_convertida = float(request.form["cantidadConvertidaEditar"])
        
        cur = mysql.connection.cursor()
        try:
            # Actualizar el formato
            cur.execute(
                "UPDATE formatosRecetas SET nombreFormato = %s WHERE idFormato = %s",
                (nombre_formato, id_formato)
            )
            
            # Actualizar la relación insumo-formato
            cur.execute(
                "UPDATE insumoFormatos SET cantidadConvertida = %s WHERE idFormatoFK = %s",
                (cantidad_convertida, id_formato)
            )
            
            mysql.connection.commit()
            flash("Formato actualizado correctamente", "formato_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al actualizar formato", "formato_error")
        finally:
            cur.close()
            
        return redirect(url_for("gestion_insumos"))

@app.route("/eliminarFormatoReceta", methods=["POST"])
def eliminar_formato_receta():
    if request.method == "POST":
        id_formato = request.form["idFormatoEliminar"]
        
        cur = mysql.connection.cursor()
        try:
            #eliminar la relacion insumo-formato
            cur.execute(
                "DELETE FROM insumoFormatos WHERE idFormatoFK = %s",
                (id_formato,)
            )
            
            # eliminar el formato
            cur.execute(
                "DELETE FROM formatosRecetas WHERE idFormato = %s",
                (id_formato,)
            )
            
            mysql.connection.commit()
            flash("Formato eliminado correctamente", "formato_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al eliminar formato", "formato_error")
        finally:
            cur.close()
            
        return redirect(url_for("gestion_insumos"))
