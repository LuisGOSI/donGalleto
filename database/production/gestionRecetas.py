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
        "nombre": f"{row[1]} ({row[2]})",
        "unidadBase": row[2]
    } for row in cur.fetchall()]
    cur.close()
    
    return (insumos)

@app.route('/api/insumos/<int:id_insumo>/formatos')
def get_formatos_insumo(id_insumo):
    
    cur = mysql.connection.cursor()
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
        "equivalencia": row[2]
    } for row in cur.fetchall()]
    cur.close()
    
    return (formatos)