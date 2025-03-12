from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash 
from werkzeug.security import generate_password_hash 

app = Flask(__name__)
# Llave secreta para la sesion
app.config['SECRET_KEY'] = '92r8yhfwn;02h3radf'
# Configuracion de la base de datos
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "dongalleto"


# Inicializacion de la base de datos
mysql = MySQL(app)


# Rutas -------------------------------------------------------------------------------------------------------------
@app.route("/sobreNosotros")
def about_us():
    user = session.get('user')
    if user is not None:
        return render_template("/pages/about_us.html", user=user)
    else:
        return render_template("/pages/about_us.html", user=None)



# Login -------------------------------------------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("/pages/home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    user = session.get('user')
    if user is not None:
        return redirect(url_for('about_us'))
    else:   
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM ussertest where email = %s", (email,))
            userDb = cur.fetchone()
            cur.close()
            if userDb and check_password_hash(userDb[3], password):
                session["user"] = userDb
                print(user)
                session["role"] = userDb[5]
                role = userDb[5]
                if role == "administrador":
                    return redirect(url_for("admin_dashboard"))
                elif role == "produccion":
                    return redirect(url_for("produccion_dashboard"))
                elif role == "vendedor":
                    return redirect(url_for("ventas_dashboard"))
                else:
                    return redirect(url_for("cliente_dashboard"))

            else:
                return render_template("/pages/login.html") # Si falla la autenticación, recarga el login
        return render_template("/pages/login.html")   # Si es GET, muestra el formulario de login


#Registro de usuario
@app.route("/register", methods=["POST"])
def registerUser():
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
        return redirect(url_for("about_us"))


# Registro de admin
@app.route("/registroAdmin", methods=["POST", "GET"])
def registerAdmin():
    active_user = session.get("user")
    if active_user and session.get("role") != "administrador":
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        phone = request.form["phone"]
        role = request.form["role"]
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO ussertest (name, email, password, phone, role) VALUES (%s, %s, %s, %s, %s)",
        (name, email, password, phone, role),)
        mysql.connection.commit()  
        cur.close()
        flash("Usuario registrado con éxito")
        return redirect(url_for("registerAdmin"))
    return render_template("/pages/admin/registerAdmin.html")




# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop('user')
    return redirect(url_for('login'))

# Test -------------------------------------------------------------------------------------------------------------
@app.route("/test")
def test():
    return render_template("/pages/test.html")

@app.route("/admin")
def admin_dashboard():
    return render_template("/pages/admin/admin_dashboard.html")

@app.route("/produccion")
def produccion_dashboard():
    return "Bienvenido al panel de producción"

@app.route("/ventas")
def ventas_dashboard():
    return "Bienvenido al panel de ventas"

@app.route("/cliente")
def cliente_dashboard():
    return "Bienvenido al panel de cliente"
