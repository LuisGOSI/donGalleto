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
            cur.execute("SELECT * FROM usuarios where usuario = %s", (email,))
            userDb = cur.fetchone()
            cur.close()
            if userDb and check_password_hash(userDb[2], password):
                session["user"] = userDb
                session["role"] = userDb[3]
                role = userDb[3]
                if role == "Administrador":
                    return redirect(url_for("admin_dashboard"))
                elif role == "Produccion":
                    return redirect(url_for("produccion_dashboard"))
                elif role == "Vendedor":
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
        nombre = request.form["name"]
        telefono = request.form["phone"]
        usuario = request.form["email"]
        contraseña = generate_password_hash(request.form["password"])
        
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO clientes (nombreCliente, telefono) VALUES (%s, %s)",
            (nombre, telefono)
        )
        idCliente = cur.lastrowid  # Obtener el ID del cliente recién insertado
        
        cur.execute(
            "INSERT INTO usuarios (usuario, contraseña, rol, idClienteFK) VALUES (%s, %s, 'Cliente', %s)",
            (usuario, contraseña, idCliente)
        )
        
        mysql.connection.commit()
        cur.close()
        
        session["user"] = usuario
        return redirect(url_for("about_us"))


# Registro de admin
@app.route("/registroAdmin", methods=["POST", "GET"])
def registerAdmin():
    print(session.get("role"))
    if session.get("role") != "Administrador":
        session.pop('role')
        session.pop('user')
        return redirect(url_for("login"))
    if request.method == "POST":
        nombre = request.form["name"]
        apellidoP = request.form["apellidoP"]
        apellidoM = request.form["apellidoM"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        puesto = request.form["puesto"]
        cur = mysql.connection.cursor()
        

        cur.execute(
            "INSERT INTO empleado (nombreEmpleado, puesto, apellidoP, apellidoM) VALUES (%s, %s, %s, %s)",
            (nombre, puesto, apellidoP, apellidoM)
        )
        idEmpleado = cur.lastrowid 
        
        cur.execute(
            "INSERT INTO usuarios (usuario, contraseña, rol, idEmpleadoFK) VALUES (%s, %s, %s, %s)",
            (email, password, role, idEmpleado)
        )
        
        mysql.connection.commit()  
        cur.close() 
        flash("Usuario registrado con éxito")
        return redirect(url_for("registerAdmin"))
    empleados=get_empleados()
    print(empleados)
    return render_template("/pages/admin/registerAdmin.html", empleado=empleados)




# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop('user')
    session.pop('role')
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

def get_empleados():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT e.idEmpleado, e.nombreEmpleado, e.apellidoP, e.apellidoM, e.puesto, 
               u.usuario, u.rol 
        FROM empleado e
        JOIN usuarios u ON e.idEmpleado = u.idEmpleadoFK
    """)
    empleados = cur.fetchall()
    cur.close()
    return empleados