from flask import Flask
from flask_mysqldb import MySQL
import os


app = Flask(__name__)
# Llave secreta para la sesion
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
# Configuracion de la base de datos
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = "dongalletodev"

mysql = MySQL(app)