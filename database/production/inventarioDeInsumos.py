from flask import request, redirect, url_for, flash, jsonify
from db import app, mysql

def getInvInsumosTabla():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM vistaInventarioInsumos")
    insumosTabla = cursor.fetchall()
    cursor.close()
    return insumosTabla


def obtener_insumos():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            idInsumo, 
            nombreInsumo,
            unidadMedida
        FROM insumos
    """)
    insumos = cursor.fetchall()
    cursor.close()
    return insumos


def obtener_presentaciones_por_insumo(id_insumo):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            p.idPresentacion, 
            p.nombrePresentacion, 
            p.cantidadBase, 
            i.unidadMedida
        FROM presentacionesinsumos p
        JOIN insumos i ON p.idInsumoFK = i.idInsumo
        WHERE p.idInsumoFK = %s
    """, (id_insumo,))
    presentaciones = cursor.fetchall()
    cursor.close()
    return presentaciones


def getInsumosResumen():
    cur = mysql.connection.cursor()
    cur.execute("SELECT producto, cantidad_disponible, fecha_caducidad FROM dongalletodev.vistainventarioinsumos;")
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


@app.route('/getInsumos')
def get_insumos():
    insumos = obtener_insumos()
    return jsonify([{
        'idInsumo': insumo[0],    
        'nombreInsumo': insumo[1],
        'unidadMedida': insumo[2] 
    } for insumo in insumos])


@app.route('/getPresentacionesPorInsumo/<int:id_insumo>')
def get_presentaciones_por_insumo(id_insumo):
    presentaciones = obtener_presentaciones_por_insumo(id_insumo)
    return jsonify([{
        'idPresentacion': presentacion[0],
        'nombrePresentacion': presentacion[1],
        'cantidadBase': presentacion[2],
        'unidadMedida': presentacion[3]
    } for presentacion in presentaciones])


@app.route("/registrarInsumo", methods=["POST"])
def registrarInsumo():
    if request.method == "POST":
        idPresentacionFK = request.form["idPresentacionFK"]
        cantidadCompra = float(request.form["cantidadCompra"])
        fechaCaducidad = request.form["fechaCaducidad"]
        cur = mysql.connection.cursor()
        try:
            # Obtén detalles de la presentación
            cur.execute("""
                SELECT i.idInsumo, p.cantidadBase, i.nombreInsumo 
                FROM presentacionesinsumos p
                JOIN insumos i ON p.idInsumoFK = i.idInsumo
                WHERE p.idPresentacion = %s
            """, (idPresentacionFK,))
            resultado = cur.fetchone()
            if resultado:
                idInsumoFK = resultado[0]
                cantidadBase = resultado[1]
                nombreInsumo = resultado[2]
                # Calcula la cantidad total en la unidad base
                cantidadTotalBase = cantidadCompra * cantidadBase
                # Inserta en inventario de insumos
                cur.execute(
                    "INSERT INTO inventarioInsumos (idInsumoFK, cantidad, fechaCaducidad) VALUES (%s, %s, %s)",
                    (idInsumoFK, cantidadTotalBase, fechaCaducidad),
                )
                mysql.connection.commit()
                flash(f"Insumo registrado exitosamente. {cantidadCompra} {nombreInsumo} agregados (Total: {cantidadTotalBase} unidades base).", "success")
            else:
                flash("No se encontró la presentación del insumo.", "danger")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al registrar el insumo: {str(e)}", "danger")
        finally:
            cur.close()
        return redirect(url_for("insumos_inventory"))
