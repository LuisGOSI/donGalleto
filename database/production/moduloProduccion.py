from db import app, mysql
from flask import jsonify

@app.route('/buscarRecetasPorId/<int:galleta_id>')
def buscar_recetas_por_id(galleta_id):
    cursor = mysql.connection.cursor()    
    # Obtener información básica de la galleta
    cursor.execute("SELECT nombreGalleta FROM galletas WHERE idGalleta = %s", (galleta_id,))
    galleta = cursor.fetchone()
    
    if not galleta:
        return jsonify({'error': 'Galleta no encontrada'}), 404
    
    # Obtener recetas para esta galleta
    cursor.execute("""
        SELECT r.idReceta, r.nombreReceta 
        FROM recetas r 
        WHERE r.idGalletaFK = %s AND r.estatus = 1
    """, (galleta_id,))
    recetas = cursor.fetchall()
    
    resultados = {
        'galleta': galleta[0],
        'recetas': []
    }
    
    # Para cada receta, obtener sus ingredientes
    for receta in recetas:
        cursor.execute("""
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
        """, (receta[0],))
        ingredientes = cursor.fetchall()
        
        resultados['recetas'].append({
            'id': receta[0],
            'nombre': receta[1],
            'ingredientes': [{
                'nombre': ing[0],
                'unidad': ing[1],
                'cantidad_formato': ing[2],
                'formato': ing[3],
                'tiene_conversion': bool(ing[5]),  # Convertir a booleano
                'cantidad_exacta': ing[6],
                'descripcion': (f"{ing[2]} {ing[3]} de {ing[0]} ({ing[6]} {ing[1]}{'s' if ing[6] > 1 else ''})"
                                if bool(ing[5]) 
                                else f"{ing[2]} {ing[3]} de {ing[0]}")
            } for ing in ingredientes]
        })
    
    return jsonify(resultados)


@app.route('/verificar-insumos/<int:receta_id>')
def verificar_insumos(receta_id):
    cursor = mysql.connection.cursor()    
    # Obtener los ingredientes necesarios y los insumos disponibles
    cursor.execute("""
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
    """, (receta_id,))
    
    ingredientes = cursor.fetchall()
    faltantes = []
    
    for ing in ingredientes:
        cantidad_necesaria = ing[5] if ing[4] is not None else ing[3]
        cantidad_disponible = ing[6] or 0
        
        if cantidad_disponible < cantidad_necesaria:
            faltantes.append({
                'nombre': ing[1],
                'necesario': cantidad_necesaria,
                'disponible': cantidad_disponible,
                'unidad': ing[2]
            })
    
    return jsonify({
        'suficiente': len(faltantes) == 0,
        'faltantes': faltantes,
        'receta_id': receta_id
    })