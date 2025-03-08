from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash 
from werkzeug.security import generate_password_hash 

app = Flask(__name__)
# Llave secreta para la sesion
app.config['SECRET_KEY'] = '92r8yhfwn;02h3radf'
# Configuracion de la base de datos
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "cisco123"
app.config["MYSQL_DB"] = "dongalleto"


# Inicializacion de la base de datos
mysql = MySQL(app)


# Rutas -------------------------------------------------------------------------------------------------------------
@app.route("/sobreNosotros")
def index():
    if 'user' in session:
        return render_template("/pages/about_us.html")
    else:
        return redirect(url_for("login"))


# Login -------------------------------------------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("/pages/home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    else:   
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM ussertest where email = %s", (email,))
            user = cur.fetchone()
            print(user)
            cur.close()
            if user and check_password_hash(user[4], password):
                session["user"] = user[2]
                return redirect(url_for("index"))
            else:
                return render_template("/pages/login.html")
        return render_template("/pages/login.html")



# Registro de usuario
@app.route("/register", methods=["POST"])
def testDb():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        phone = request.form["phone"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO ussertest (name, email, password, phone) VALUES (%s, %s, %s, %s)",
            (name, email, password, phone),
        )
        cur.execute("SELECT * FROM ussertest where name = %s and password = %s", (name,password))
        user = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        session["user"] = user[2]
        return redirect(url_for("index"))


# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Test -------------------------------------------------------------------------------------------------------------
@app.route("/test")
def test():
    return render_template("/pages/test.html")