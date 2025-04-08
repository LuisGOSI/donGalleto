from flask import request, redirect, url_for, flash, session
from db import app,mysql  

@app.route("/api/inventario-galleta/<int:id_galleta>")
def get_inventario_galleta(id_galleta):
    
    cur = mysql.connection.cursor()
    try:
        # Obtener todos los lotes disponibles de esta galleta
        query = """
        SELECT ig.cantidadGalletas 
        FROM inventariogalletas ig
        JOIN produccion p ON ig.idProduccionFK = p.idProduccion
        JOIN recetas r ON p.idRecetaFK = r.idReceta
        WHERE r.idGalletaFK = %s AND ig.estadoLote = 'Disponible'
        """
        cur.execute(query, (id_galleta,))
        lotes = cur.fetchall()
        
        return ({
            "success": True,
            "inventario": [{"cantidadGalletas": lote[0]} for lote in lotes]
        })
    except Exception as e:
        return ({"success": False, "message": str(e)}), 500
    finally:
        cur.close()

@app.route("/api/recetas-galleta/<int:id_galleta>")
def get_recetas_galleta(id_galleta):

    cur = mysql.connection.cursor()
    try:
        # Obtener todas las recetas activas para esta galleta
        query = """
        SELECT idReceta, nombreReceta, cantidadHorneadas 
        FROM recetas 
        WHERE idGalletaFK = %s AND estatus = 1
        """
        cur.execute(query, (id_galleta,))
        recetas = cur.fetchall()
        return ({
            "success": True,
            "recetas": [{
                "idReceta": receta[0],
                "nombreReceta": receta[1],
                "cantidadHorneadas": receta[2]
            } for receta in recetas]
        })
    except Exception as e:
        return ({"success": False, "message": str(e)}), 500
    finally:
        cur.close()


@app.route("/api/solicitudes-pendientes/<int:id_galleta>")
def get_solicitudes_pendientes(id_galleta):
    
    cur = mysql.connection.cursor()
    try:
        # Contar producciones pendientes para esta galleta
        query = """
        SELECT COUNT(*) 
        FROM produccion p
        JOIN recetas r ON p.idRecetaFK = r.idReceta
        WHERE r.idGalletaFK = %s AND p.estadoProduccion = 'Solicitud'
        """
        cur.execute(query, (id_galleta,))
        count = cur.fetchone()[0]
        
        return ({
            "success": True,
            "pendientes": count
        })
    except Exception as e:
        return ({"success": False, "message": str(e)}), 500
    finally:
        cur.close()

@app.route("/api/crear-produccion", methods=["POST"])
def crear_produccion():

    data = request.get_json()
    id_receta = data.get('idReceta')
    cantidad = data.get('cantidad')
    
    if not id_receta or not cantidad:
        return ({"success": False, "message": "Datos incompletos"}), 400
    
    cur = mysql.connection.cursor()
    try:
        # Insertar nueva producción con estado "Solicitud"
        query = """
        INSERT INTO produccion (idRecetaFK, fechaProduccion, estadoProduccion)
        VALUES (%s, NOW(), 'Solicitud')
        """
        cur.execute(query, (id_receta,))
        mysql.connection.commit()
        
        return ({
            "success": True,
            "message": "Solicitud de producción creada exitosamente"
        })
    except Exception as e:
        mysql.connection.rollback()
        return ({"success": False, "message": str(e)}), 500
    finally:
        cur.close()