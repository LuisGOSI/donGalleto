from dotenv import load_dotenv
from db import mysql  

load_dotenv()


def getPresentaciones():
    cur = mysql.connection.cursor()
    cur.execute("""
SELECT 
    dv.tipoVenta,
    SUM(dv.cantidad_galletas * dv.PrecioUnitarioVendido * (1 - v.descuento/100)) AS dinero_ganado_real
FROM detalleventas dv
JOIN ventas v ON dv.idVentaFK = v.idVenta
GROUP BY dv.tipoVenta
ORDER BY dinero_ganado_real DESC;
    """)
    presentaciones = [{"tipoVenta": row[0], "total": row[1]} for row in cur.fetchall()]
    cur.close()
    return presentaciones


def getGanancias():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
        DATE(v.fechaVenta) AS fecha,
        SUM(dv.cantidad_galletas * dv.PrecioUnitarioVendido * (1 - v.descuento/100)) AS ingresos_totales_diarios
        FROM ventas v
        JOIN detalleventas dv ON v.idVenta = dv.idVentaFK
        WHERE v.fechaVenta >= CURDATE() - INTERVAL 4 DAY
        GROUP BY DATE(v.fechaVenta)
        ORDER BY fecha DESC;
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


def getInversionGalletas():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM dongalletodev.inversionpotencial;
    """)
    inversion = [{"inversion": row[0],"Ganancias": row[1]} for row in cur.fetchall()]
    cur.close()
    return inversion

def getGalletaRecomendad():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nombreGalleta,imagen,total_existencias FROM dongalletodev.galletarecomendada;
    """)
    recomendad = [{"nombreGalleta": row[0],"imagen": row[1],"total_existencias":row[2]} for row in cur.fetchall()]
    cur.close()
    return recomendad