from flask import request, redirect, url_for, flash
from db import app,mysql  
from dotenv import load_dotenv

@app.route('/api/galletas')
def get_galletas():
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT idGalleta, nombreGalleta FROM galletas ORDER BY nombreGalleta")
    galletas = [{"id": row[0], "nombre": row[1]} for row in cur.fetchall()]
    cur.close()
    
    return (galletas)

@app.route('/api/insumos')
def get_insumos_recetas():
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.idInsumo, i.nombreInsumo, i.unidadMedida 
        FROM insumos i
        ORDER BY i.nombreInsumo
    """)
    insumos = [{
        "id": row[0], 
        "nombre": row[1],
        "unidadBase": row[2]
    } for row in cur.fetchall()]
    cur.close()
    
    return (insumos)

@app.route('/api/insumos/<int:id_insumo>/formatos')
def get_formatos_insumo(id_insumo):
    cur = mysql.connection.cursor()
    
    # Obtener la unidad base del insumo primero
    cur.execute("SELECT unidadMedida FROM insumos WHERE idInsumo = %s", (id_insumo,))
    unidad_base = cur.fetchone()[0]
    
    # Obtener los formatos
    cur.execute("""
        SELECT fr.idFormato, fr.nombreFormato, ifr.cantidadConvertida
        FROM formatosRecetas fr
        JOIN insumoFormatos ifr ON fr.idFormato = ifr.idFormatoFK
        WHERE ifr.idInsumoFK = %s
        ORDER BY fr.nombreFormato
    """, (id_insumo,))
    
    formatos = [{
        "id": row[0],
        "nombre": row[1],
        "equivalencia": row[2],
        "unidadBase": unidad_base
    } for row in cur.fetchall()]
    
    cur.close()
    return (formatos)


@app.route('/registerReceta', methods=['POST'])
def registerReceta():
    if request.method == "POST":
        # Datos básicos de la receta
        nombreReceta = request.form.get("nombreReceta")
        idGalletaFK = request.form.get("idGalletaFK")
        cantidadHorneadas = request.form.get("cantidadHorneadas")
        duracionAnaquel = request.form.get("duracionAnaquel")
        
        cur = mysql.connection.cursor()
        try:
            # Insertar la receta en la tabla recetas
            query_receta = """
                INSERT INTO recetas (idGalletaFK, nombreReceta, cantidadHorneadas, duracionAnaquel)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(query_receta, (idGalletaFK, nombreReceta, cantidadHorneadas, duracionAnaquel))
            mysql.connection.commit()
            # Obtener el ID de la receta recién insertada
            idReceta = cur.lastrowid

            # Procesar los detalles de la receta
            detalles = []
            # Buscamos todas las claves que correspondan a detalles del insumo
            for key in request.form.keys():
                if key.startswith("detalles[") and key.endswith("][idInsumoFK]"):
                    # Extraemos el índice del detalle
                    index = key.split("[")[1].split("]")[0]
                    idInsumoFK = request.form.get(f"detalles[{index}][idInsumoFK]")
                    idFormatoFK = request.form.get(f"detalles[{index}][idUnidadFK]")
                    cantidadFormato = request.form.get(f"detalles[{index}][cantidadFormato]")
                    # Agregar el detalle a la lista
                    detalles.append((idReceta, idInsumoFK, idFormatoFK, cantidadFormato))

            # Insertar los detalles si existen
            if detalles:
                query_detalle = """
                    INSERT INTO detallereceta (idRecetaFK, idInsumoFK, idFormatoFK, cantidadFormato)
                    VALUES (%s, %s, %s, %s)
                """
                cur.executemany(query_detalle, detalles)
                mysql.connection.commit()
            
            flash("Receta registrada exitosamente", "receta_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al registrar receta", "receta_error")
        finally:
            cur.close()
        
        return redirect(url_for("receta"))
    
@app.route("/api/recetas/<int:id_receta>/detalles")
def get_detalles_receta(id_receta):

    cur = mysql.connection.cursor()
    
    try:
        # Obtener información básica de la receta
        cur.execute("""
            SELECT r.nombreReceta, r.cantidadHorneadas, r.duracionAnaquel, 
                   g.nombreGalleta
            FROM recetas r
            JOIN galletas g ON r.idGalletaFK = g.idGalleta
            WHERE r.idReceta = %s AND r.estatus = 1
        """, (id_receta,))
        receta_data = cur.fetchone()
        
        if not receta_data:
            return {"error": "Receta no encontrada"}, 404
        
        # Obtener detalles de ingredientes con información de formatos
        cur.execute("""
            SELECT i.nombreInsumo, fr.nombreFormato, dr.cantidadFormato, i.unidadMedida
            FROM detallereceta dr
            JOIN insumos i ON dr.idInsumoFK = i.idInsumo
            JOIN formatosRecetas fr ON dr.idFormatoFK = fr.idFormato
            JOIN recetas r ON dr.idRecetaFK = r.idReceta
            WHERE dr.idRecetaFK = %s AND r.estatus = 1
            ORDER BY i.nombreInsumo
        """, (id_receta,))
        
        detalles = cur.fetchall()
        
        # Formatear la respuesta
        response = {
            "nombreReceta": receta_data[0],
            "cantidadHorneadas": receta_data[1],
            "duracionAnaquel": receta_data[2],
            "nombreGalleta": receta_data[3],
            "ingredientes": [
                {
                    "nombreInsumo": detalle[0],
                    "formato": detalle[1],
                    "cantidad": float(detalle[2]),
                    "unidadMedida": detalle[3]
                }
                for detalle in detalles
            ]
        }
        
        return (response)
        
    except Exception as e:
        return {"error": str(e)}, 500
        
    finally:
        cur.close()


@app.route("/api/recetas/<int:id_receta>/editar")
def get_receta_para_editar(id_receta):
    cur = mysql.connection.cursor()
    
    try:
        # Obtener información básica de la receta
        cur.execute("""
            SELECT r.idReceta, r.nombreReceta, r.cantidadHorneadas, r.duracionAnaquel, 
                   r.idGalletaFK, g.nombreGalleta
            FROM recetas r
            JOIN galletas g ON r.idGalletaFK = g.idGalleta
            WHERE r.idReceta = %s
        """, (id_receta,))
        receta_data = cur.fetchone()
        
        if not receta_data:
            return {"error": "Receta no encontrada"}, 404
        
        # Obtener detalles de ingredientes
        cur.execute("""
            SELECT dr.idInsumoFK, dr.idFormatoFK, dr.cantidadFormato,
                   i.nombreInsumo, i.unidadMedida,
                   fr.nombreFormato
            FROM detallereceta dr
            JOIN insumos i ON dr.idInsumoFK = i.idInsumo
            JOIN formatosRecetas fr ON dr.idFormatoFK = fr.idFormato
            WHERE dr.idRecetaFK = %s
            ORDER BY i.nombreInsumo
        """, (id_receta,))
        detalles = cur.fetchall()
        
        # Formatear la respuesta
        response = {
            "idReceta": receta_data[0],
            "nombreReceta": receta_data[1],
            "cantidadHorneadas": receta_data[2],
            "duracionAnaquel": receta_data[3],
            "idGalletaFK": receta_data[4],
            "nombreGalleta": receta_data[5],
            "ingredientes": [
                {
                    "idInsumoFK": detalle[0],
                    "idUnidadFK": detalle[1],
                    "cantidadFormato": float(detalle[2]),
                    "nombreInsumo": detalle[3],
                    "unidadMedida": detalle[4],
                    "nombreFormato": detalle[5]
                }
                for detalle in detalles
            ]
        }
        
        return (response)
        
    except Exception as e:
        return {"error": str(e)}, 500
        
    finally:
        cur.close()

@app.route('/updateReceta', methods=['POST'])
def updateReceta():
    if request.method == "POST":
        # Datos básicos de la receta
        idReceta = request.form.get("idReceta")
        nombreReceta = request.form.get("nombreReceta")
        idGalletaFK = request.form.get("idGalletaFK")
        cantidadHorneadas = request.form.get("cantidadHorneadas")
        duracionAnaquel = request.form.get("duracionAnaquel")
        
        cur = mysql.connection.cursor()
        try:
            # Actualizar la receta en la tabla recetas
            query_receta = """
                UPDATE recetas 
                SET idGalletaFK = %s, nombreReceta = %s, 
                    cantidadHorneadas = %s, duracionAnaquel = %s
                WHERE idReceta = %s
            """
            cur.execute(query_receta, (idGalletaFK, nombreReceta, cantidadHorneadas, duracionAnaquel, idReceta))
            
            # Eliminar los detalles antiguos
            cur.execute("DELETE FROM detallereceta WHERE idRecetaFK = %s", (idReceta,))
            
            # Procesar los nuevos detalles de la receta
            detalles = []
            for key in request.form.keys():
                if key.startswith("detalles[") and key.endswith("][idInsumoFK]"):
                    index = key.split("[")[1].split("]")[0]
                    idInsumoFK = request.form.get(f"detalles[{index}][idInsumoFK]")
                    idFormatoFK = request.form.get(f"detalles[{index}][idUnidadFK]")
                    cantidadFormato = request.form.get(f"detalles[{index}][cantidadFormato]")
                    detalles.append((idReceta, idInsumoFK, idFormatoFK, cantidadFormato))

            # Insertar los nuevos detalles si existen
            if detalles:
                query_detalle = """
                    INSERT INTO detallereceta (idRecetaFK, idInsumoFK, idFormatoFK, cantidadFormato)
                    VALUES (%s, %s, %s, %s)
                """
                cur.executemany(query_detalle, detalles)
            
            mysql.connection.commit()
            flash("Receta actualizada exitosamente", "receta_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al actualizar receta", "receta_error")
        finally:
            cur.close()
        
        return redirect(url_for("receta"))
    

@app.route("/eliminarReceta", methods=["POST"])
def eliminar_receta():
    if request.method == "POST":
        id_receta = request.form["idRecetaEliminar"]
        
        cur = mysql.connection.cursor()
        try:
            # Eliminación lógica
            cur.execute(
                "UPDATE recetas SET estatus = 0 WHERE idReceta = %s",
                (id_receta,)
            )
            
            mysql.connection.commit()
            flash("Receta desactivada correctamente", "receta_success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al eliminar receta", "receta_error")
        finally:
            cur.close()
            
        return redirect(url_for("receta"))
    