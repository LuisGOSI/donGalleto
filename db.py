from flask import Flask
from flask_mysqldb import MySQL
from flask_simple_captcha import CAPTCHA
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
# Llave secreta para la sesion
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
# Configuracion de la base de datos
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = "dongalletodev"
CAPTCHA_CONFIG = {
    'SECRET_CAPTCHA_KEY': os.getenv("CAPTCHA_SECRET_KEY"),
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': False,
    'EXPIRE_SECONDS': 120,
    'CAPTCHA_IMG_FORMAT': 'JPEG',
    'ROUTE': '/simple-captcha-image/<key>'
}
mysql = MySQL(app)
captcha = CAPTCHA(config=CAPTCHA_CONFIG)
captcha.init_app(app)
