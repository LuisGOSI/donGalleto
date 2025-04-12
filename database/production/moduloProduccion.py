from db import app, mysql
from flask import jsonify, request
from datetime import timedelta


@app.route("/buscarRecetasPorId/<int:galleta_id>")
def buscar_recetas_por_id(galleta_id):
    cursor = mysql.connection.cursor()
    # Obtener información básica de la galleta
    cursor.execute(
        "SELECT nombreGalleta FROM galletas WHERE idGalleta = %s", (galleta_id,)
    )
    galleta = cursor.fetchone()

    if not galleta:
        return jsonify({"error": "Galleta no encontrada"}), 404

    # Obtener recetas para esta galleta
    cursor.execute(
        """
        SELECT r.idReceta, r.nombreReceta 
        FROM recetas r 
        WHERE r.idGalletaFK = %s AND r.estatus = 1
    """,
        (galleta_id,),
    )
    recetas = cursor.fetchall()

    resultados = {"galleta": galleta[0], "recetas": []}

    # Para cada receta, obtener sus ingredientes
    for receta in recetas:
        cursor.execute(
            """
            SELECT 
                i.nombreInsumo,
                i.unidadMedida,
                dr.cantidadFormato,
                fr.nombreFormato,
                iform.cantidadConvertida,
                CASE
                    WHEN iform.idInsumoFK IS NULL THEN 0  # No tiene conversión
                    ELSE 1  # Sí tiene conversión
                END as tiene_conversion,
                CASE
                    WHEN iform.idInsumoFK IS NULL THEN dr.cantidadFormato
                    ELSE ROUND(dr.cantidadFormato * iform.cantidadConvertida, 2)
                END as cantidadExacta
            FROM detallereceta dr
            JOIN insumos i ON dr.idInsumoFK = i.idInsumo
            JOIN formatosrecetas fr ON dr.idFormatoFK = fr.idFormato
            LEFT JOIN insumoformatos iform ON 
                iform.idInsumoFK = i.idInsumo AND 
                iform.idFormatoFK = fr.idFormato
            WHERE dr.idRecetaFK = %s
        """,
            (receta[0],),
        )
        ingredientes = cursor.fetchall()

        resultados["recetas"].append(
            {
                "id": receta[0],
                "nombre": receta[1],
                "ingredientes": [
                    {
                        "nombre": ing[0],
                        "unidad": ing[1],
                        "cantidad_formato": ing[2],
                        "formato": ing[3],
                        "tiene_conversion": bool(ing[5]),  # Convertir a booleano
                        "cantidad_exacta": ing[6],
                        "descripcion": (
                            f"{ing[2]} {ing[3]} de {ing[0]} ({ing[6]} {ing[1]}{'s' if ing[6] > 1 else ''})"
                            if bool(ing[5])
                            else f"{ing[2]} {ing[3]} de {ing[0]}"
                        ),
                    }
                    for ing in ingredientes
                ],
            }
        )

    return jsonify(resultados)


@app.route("/verificar-insumos/<int:receta_id>")
def verificar_insumos(receta_id):
    cursor = mysql.connection.cursor()
    # Obtener los ingredientes necesarios y los insumos disponibles
    cursor.execute(
        """
        SELECT 
            i.idInsumo,
            i.nombreInsumo,
            i.unidadMedida,
            dr.cantidadFormato,
            iform.cantidadConvertida,
            ROUND(dr.cantidadFormato * iform.cantidadConvertida, 2) as cantidadNecesaria,
            (
                SELECT SUM(cantidad) 
                FROM inventarioinsumos 
                WHERE idInsumoFK = i.idInsumo 
                AND estadoLote = 'Disponible'
                AND fechaCaducidad > CURDATE()
            ) as cantidadDisponible
        FROM detallereceta dr
        JOIN insumos i ON dr.idInsumoFK = i.idInsumo
        LEFT JOIN insumoformatos iform ON 
            iform.idInsumoFK = i.idInsumo AND 
            iform.idFormatoFK = dr.idFormatoFK
        WHERE dr.idRecetaFK = %s
    """,
        (receta_id,),
    )

    ingredientes = cursor.fetchall()
    faltantes = []

    for ing in ingredientes:
        cantidad_necesaria = ing[5] if ing[4] is not None else ing[3]
        cantidad_disponible = ing[6] or 0

        if cantidad_disponible < cantidad_necesaria:
            faltantes.append(
                {
                    "nombre": ing[1],
                    "necesario": cantidad_necesaria,
                    "disponible": cantidad_disponible,
                    "unidad": ing[2],
                }
            )

    return jsonify(
        {
            "suficiente": len(faltantes) == 0,
            "faltantes": faltantes,
            "receta_id": receta_id,
        }
    )


@app.route("/producciones-en-curso")
def producciones_en_curso():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT p.idProduccion, g.nombreGalleta, r.nombreReceta, p.estadoProduccion, g.imgGalleta
        FROM produccion p
        JOIN recetas r ON p.idRecetaFK = r.idReceta
        JOIN galletas g ON r.idGalletaFK = g.idGalleta
        WHERE p.estadoProduccion != 'Listo'
    """
    )
    producciones = cur.fetchall()
    cur.close()
    return jsonify(
        {
            "producciones": [
                {
                    "idProduccion": prod[0],
                    "nombreGalleta": prod[1],
                    "nombreReceta": prod[2],
                    "estadoProduccion": prod[3],
                    "imgGalleta": prod[4],
                }
                for prod in producciones
            ]
        }
    )


@app.route("/actualizar-estado-porID/<int:id_produccion>", methods=["POST"])
def actualizar_estado_por_id(id_produccion):
    cur = mysql.connection.cursor()
    data = request.get_json()
    if not data or "nuevoEstado" not in data:
        return jsonify({"error": "Estado de producción no proporcionado"}), 400
    match data["nuevoEstado"]:
        case "Preparación":
            nuevo_estado = "Preparación"
        case "Horneado":
            nuevo_estado = "Horneado"
        case "Enfriado":
            nuevo_estado = "Enfriado"
        case "Listo":
            nuevo_estado = "Listo"
        case _:
            return jsonify({"error": "Estado de producción no válido"}), 400
    try:
        cur.execute(
            """
            UPDATE produccion 
            SET estadoProduccion = %s 
            WHERE idProduccion = %s
        """,
            (nuevo_estado, id_produccion),
        )
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Estado actualizado correctamente"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500



@app.route("/revisarDisponibilidadRecetaPorId/<int:id_receta>", methods=["POST"])
def revisar_disponibilidad_receta_por_id(id_receta):
    try:
        ingredientes = obtener_disponibilidad_receta(id_receta)
        return jsonify({"success": True, "ingredientes": ingredientes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def obtener_disponibilidad_receta(id_receta):
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            """
            WITH Requerimientos AS (
                SELECT 
                    dr.idInsumoFK AS InsumoID,
                    SUM(dr.cantidadFormato * ifm.cantidadConvertida) AS CantidadNecesaria
                FROM detallereceta dr
                JOIN insumoformatos ifm 
                    ON dr.idInsumoFK = ifm.idInsumoFK 
                    AND dr.idFormatoFK = ifm.idFormatoFK
                WHERE dr.idRecetaFK = %s
                GROUP BY dr.idInsumoFK
            ),
            InventarioOrdenado AS (
                SELECT 
                    ii.idInsumoFK,
                    ii.idInventarioInsumo,
                    ii.cantidad,
                    ii.fechaCaducidad,
                    SUM(ii.cantidad) OVER (
                        PARTITION BY ii.idInsumoFK 
                        ORDER BY ii.fechaCaducidad ASC
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS SumaAcumulada
                FROM inventarioinsumos ii
                WHERE ii.estadoLote = 'Disponible'
            )
            SELECT 
                r.InsumoID,
                i.nombreInsumo,
                i.unidadMedida,
                r.CantidadNecesaria,
                COALESCE(MAX(io.SumaAcumulada), 0) AS TotalDisponible,
                CASE 
                    WHEN COALESCE(MAX(io.SumaAcumulada), 0) >= r.CantidadNecesaria THEN 'Suficiente'
                    ELSE 'Insuficiente'
                END AS Estado
            FROM Requerimientos r
            JOIN insumos i ON r.InsumoID = i.idInsumo
            LEFT JOIN InventarioOrdenado io 
                ON r.InsumoID = io.idInsumoFK
            GROUP BY r.InsumoID, i.nombreInsumo, i.unidadMedida, r.CantidadNecesaria;
            """,
            (id_receta,)
        )
        ingredientes = [
            {
                "idInsumo": row[0],
                "nombreInsumo": row[1],
                "unidadMedida": row[2],
                "cantidadNecesaria": row[3],
                "totalDisponible": row[4],
                "estado": row[5],
            }
            for row in cur.fetchall()
        ]
        return ingredientes
    except Exception as e:
        raise e
    finally:
        cur.close()


@app.route("/revisarDisponibilidadPorProduccion/<int:id_produccion>", methods=["POST"])
def revisar_disponibilidad_por_produccion(id_produccion):
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            SELECT r.idReceta
            FROM produccion p
            JOIN recetas r ON p.idRecetaFK = r.idReceta
            WHERE p.idProduccion = %s
        """,
            (id_produccion,)
        )
        receta_id = cur.fetchone()
        cur.close()

        if not receta_id:
            return jsonify({"error": "Producción no encontrada"}), 404

        ingredientes = obtener_disponibilidad_receta(receta_id[0])
        return jsonify({"success": True, "ingredientes": ingredientes, "idReceta": receta_id[0]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/agregarProduccionPorReceta/<int:id_receta>", methods=["POST"])
def agregar_produccion(id_receta):
    conexion = mysql.connection
    data = request.get_json()
    ingredientes = data['data']['ingredientes']
    # Cambié a .get() para manejar mejor cuando idProduccion no existe
    idProduccion = data.get('idProduccion')  
    
    try:
        # Verificación de ingredientes (se mantiene igual)
        if any(ing['estado'] == 'Insuficiente' for ing in ingredientes):
            return jsonify({"success": False, "message": "Insumos insuficientes"}), 400

        with conexion.cursor() as cursor:
            # Iniciar transacción (se mantiene igual)
            conexion.begin()

            # --------------------------------------------
            # SECCIÓN MOVIDA: Procesamiento de ingredientes
            # (antes estaba mezclado con la lógica de producción)
            # --------------------------------------------
            for ingrediente in ingredientes:
                id_insumo = ingrediente['idInsumo']
                cantidad_necesaria = ingrediente['cantidadNecesaria']
                
                cursor.execute("""
                    SELECT idInventarioInsumo, cantidad 
                    FROM inventarioinsumos 
                    WHERE idInsumoFK = %s 
                    AND estadoLote = 'Disponible'
                    ORDER BY fechaCaducidad ASC
                """, (id_insumo,))
                
                lotes = cursor.fetchall()
                restante = cantidad_necesaria

                for lote in lotes:
                    id_lote, cantidad_lote = lote
                    
                    if cantidad_lote >= restante:
                        nueva_cantidad = cantidad_lote - restante
                        if nueva_cantidad == 0:
                            cursor.execute("""
                                UPDATE inventarioinsumos 
                                SET cantidad = 0, estadoLote = 'Agotado' 
                                WHERE idInventarioInsumo = %s
                            """, (id_lote,))
                        else:
                            cursor.execute("""
                                UPDATE inventarioinsumos 
                                SET cantidad = %s 
                                WHERE idInventarioInsumo = %s
                            """, (nueva_cantidad, id_lote))
                        restante = 0
                        break
                    else:
                        restante -= cantidad_lote
                        cursor.execute("""
                            UPDATE inventarioinsumos 
                            SET cantidad = 0, estadoLote = 'Agotado' 
                            WHERE idInventarioInsumo = %s
                        """, (id_lote,))

                if restante > 0:
                    conexion.rollback()
                    return jsonify({
                        "success": False,
                        "message": f"Insumo ID {id_insumo} insuficiente después de procesar todos los lotes"
                    }), 400

            # --------------------------------------------------
            # SECCIÓN REORGANIZADA: Manejo de la producción
            # (antes estaba DENTRO del bucle de ingredientes)
            # --------------------------------------------------
            if idProduccion is None:
                # Crear NUEVA producción (esto solo debe ejecutarse UNA vez)
                cursor.execute("""
                    INSERT INTO produccion (idRecetaFK, fechaProduccion, estadoProduccion) 
                    VALUES (%s, NOW(), 'Preparación')
                """, (id_receta,))
                # Agregado: Obtenemos el ID de la nueva producción
                idProduccion = cursor.lastrowid  
            else:
                # Actualizar producción EXISTENTE (esto solo debe ejecutarse UNA vez)
                cursor.execute("""
                    UPDATE produccion 
                    SET estadoProduccion = 'Preparación' 
                    WHERE idProduccion = %s
                """, (idProduccion,))

            # Confirmar transacción
            conexion.commit()
            
            # Retornamos el idProduccion para referencia del cliente
            return jsonify({
                "success": True, 
                "message": "Producción agregada correctamente",
                "idProduccion": idProduccion  # Nuevo: retornamos el ID
            }), 200

    except Exception as e:
        conexion.rollback()
        return jsonify({"success": False, "message": str(e)}), 500




@app.route("/agregarLotePorProduccion/<int:id_produccion>", methods=["POST"])
def agregar_lote_por_produccion(id_produccion):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT p.idRecetaFK, p.fechaProduccion, r.cantidadHorneadas, r.duracionAnaquel
            FROM produccion p
            JOIN recetas r ON p.idRecetaFK = r.idReceta
            WHERE p.idProduccion = %s
        """, (id_produccion,))
        produccion = cur.fetchone()
        if not produccion:
            return jsonify({"error": "Producción no encontrada"}), 404
        
        id_receta, fecha_produccion, cantidad_galletas, duracion_anaquel = produccion
        fecha_caducidad = fecha_produccion + timedelta(days=duracion_anaquel)

        cur.execute("""
            INSERT INTO inventariogalletas 
                (idProduccionFK, fechaCaducidad, cantidadGalletas, estadoLote)
            VALUES (%s, %s, %s, 'Disponible')
        """, (id_produccion, fecha_caducidad, cantidad_galletas))
        
        
        mysql.connection.commit()
        return jsonify({"success": True, "message": "Lote agregado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/cancelar-produccion/<int:id_produccion>", methods=["POST"])
def cancelar_produccion(id_produccion):
    try:
        cur = mysql.connection.cursor()
        
        # Eliminar producción
        cur.execute("""
            DELETE FROM produccion 
            WHERE idProduccion = %s
        """, (id_produccion,))
        
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Producción cancelada'})
        
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cur.close()