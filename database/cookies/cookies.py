from db import mysql

#Funcion para obtener todas las galletas de la base de datos (modulos: ventas, clientes)
def getCookies():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM galletas')
    data = cur.fetchall()
    cur.close()
    return data
