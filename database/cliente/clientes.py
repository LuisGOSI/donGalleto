from flask import render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

from db import app,mysql  

def getHistoricoClientes(estado=1):
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