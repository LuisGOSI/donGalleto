from dotenv import load_dotenv
from db import mysql,app
from flask import render_template, session

load_dotenv()


@app.route("/corteVentas")
def corteVentas():
    datos = getTotalGeneral()
    ventas = getDesgloseVenta()
    user = session.get("user")
    return render_template("/sales/corteVenta.html", datos=datos, user=user, ventas=ventas)

def getDesgloseVenta():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dongalletodev.desgloseventasdia;")
    datos = cur.fetchall()
    column_names = [desc[0] for desc in cur.description] 
    cur.close()
    
    ventas = [dict(zip(column_names, fila)) for fila in datos]
    return ventas


def getTotalGeneral():
    cur = mysql.connection.cursor()
    cur.execute("""
       SELECT * FROM dongalletodev.corteventadia;
    """)
    datos = cur.fetchall()
    column_names = [desc[0] for desc in cur.description] 
    cur.close()
    datos = [dict(zip(column_names, fila)) for fila in datos]
    total_ganancias = 0
    total_ventas = 0
    total_descuentos = 0
    total_ganancias_netas = 0
    for fila in datos:
        total_ganancias += fila['GananciasTotales']
        total_ventas += fila['VentasRealizadas']
        total_descuentos += fila['DescuentoAplicado']
        total_ganancias_netas += fila['GananciasNetas']
    totales = {
        'GananciasTotales': total_ganancias,
        'VentasRealizadas': total_ventas,
        'DescuentoAplicado': total_descuentos,
        'GananciasNetas': total_ganancias_netas
    }
    return totales
