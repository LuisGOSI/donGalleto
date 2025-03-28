from dotenv import load_dotenv
from db import mysql  

load_dotenv()


def getPresentaciones():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT tipoVenta, COUNT(*) as total
        FROM detalleventas
        GROUP BY tipoVenta
        ORDER BY total DESC;
    """)
    presentaciones = [{"tipoVenta": row[0], "total": row[1]} for row in cur.fetchall()]
    cur.close()
    return presentaciones

def getGanancias():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT tipoVenta, COUNT(*) as total
        FROM detalleventas
        GROUP BY tipoVenta
        ORDER BY total DESC;
    """)
    presentaciones = [{"tipoVenta": row[0], "total": row[1]} for row in cur.fetchall()]
    cur.close()
    return presentaciones

def getGanancias():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM dongalletodev.ventaspordia;
    """)
    ganancias = [{"fecha": row[0].strftime('%d-%m-%Y'), "ganancias_diarias": row[1]} for row in cur.fetchall()]
    cur.close()
    return ganancias

def getGalletasTop():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM dongalletodev.ventasgalletas;
    """)
    galletas = cur.fetchall()
    cur.close()
    return galletas
