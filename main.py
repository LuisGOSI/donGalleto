from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
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


# Inicializacion de la base de datos
mysql = MySQL(app)


# Login -------------------------------------------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    user = session.get("user")
    if user is not None:
        return redirect(url_for("cliente_dashboard"))
    else:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios where email = %s", (email,))
            userDb = cur.fetchone()
            print(userDb)
            cur.close()
            if userDb and check_password_hash(userDb[3], password):
                session["user"] = userDb
                role = userDb[4]
                if role == "administrador":
                    return redirect(url_for("admin_dashboard"))
                elif role == "produccion":
                    return redirect(url_for("produccion_dashboard"))
                elif role == "vendedor":
                    return redirect(url_for("ventas_dashboard"))
                else:
                    return redirect(url_for("cliente_dashboard"))
            else:
                return render_template(
                    "/pages/login.html"
                )  # Si falla la autenticación, recarga el login
        return render_template(
            "/pages/login.html"
        )  # Si es GET, muestra el formulario de login


# Registro de usuario
@app.route("/register", methods=["POST"])
def registerUser():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        phone = request.form["phone"]
        role = request.form["role"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO clientes (nombreCliente, telefono) VALUES (%s, %s)",
            (name, phone),
        )
        idCliente = cur.lastrowid 
        cur.execute(
            "INSERT INTO usuarios (email, password, rol, idClienteFK) VALUES (%s, %s, %s, %s)",
            (email, password, role, idCliente),
        )
        cur.execute(
            "SELECT * FROM usuarios where email = %s",
            (email,),
        )
        user = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        session["user"] = user
        return redirect(url_for("about_us"))


# Registro de admin
@app.route("/registroAdmin", methods=["POST", "GET"])
def registerAdmin():
    active_user = session.get("user")
    if active_user and active_user[4] != "administrador":
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        phone = request.form["phone"]
        role = request.form["role"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO ussertest (name, email, password, phone, role) VALUES (%s, %s, %s, %s, %s)",
            (name, email, password, phone, role),
        )
        mysql.connection.commit()
        cur.close()
        flash("Usuario registrado con éxito")
        return redirect(url_for("registerAdmin"))
    return render_template("/pages/admin/registerAdmin.html")


# Logout
@app.route("/logout", methods=["POST"])
def logout():
    if session.get("user") is not None:
        session.pop("user")
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

# Checar sesion
@app.route("/checkSession", methods=["POST"])
def checkSession():
    user_active = session.get("user")
    if user_active is not None:
        return render_template("/pages/test.html", user=user_active)
    else:
        return render_template("/pages/test.html", user=user_active)


# Rutas -------------------------------------------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("/pages/home.html")


@app.route("/sobreNosotros")
def about_us():
    user = session.get("user")
    if user is not None:
        return render_template("/pages/about_us.html", user=user)
    else:
        return render_template("/pages/about_us.html", user=None)


# Test -------------------------------------------------------------------------------------------------------------
@app.route("/test")
def test():
    return render_template("/pages/test.html")


@app.route("/admin")
def admin_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))
    user = session.get("user")
    if user[4] != "administrador":
        return redirect(url_for("login"))
    return render_template("/pages/admin/admin_dashboard.html")


@app.route("/produccion")
def produccion_dashboard():
    return render_template("/pages/production/baseProduccion/baseProduccion.html", is_base_template=True)

@app.route('/inventario-insumos')
def insumos_inventory():
    return render_template('pages/production/InveInsumos.html', is_base_template=False)

@app.route("/proveedores")
def proveedores():
    return render_template('pages/production/Proveedores.html', is_base_template = False)


@app.route("/ventas")
def ventas_dashboard():
    return "Bienvenido al panel de ventas"


@app.route("/cliente")
def cliente_dashboard():
    return "Bienvenido al panel de cliente"

# Ruta de CRUD Insumos
@app.route("/CRUD_Insumos")
def CRUD_Insumos():
    cur = mysql.connection.cursor()

    # consulta para traer los prov
    cur.execute("SELECT idProveedor, nombreProveedor FROM proveedores")
    proveedores = cur.fetchall()

    # cargar los insumos
    cur.execute("""
        SELECT 
            i.idInsumo, 
            i.nombreInsumo, 
            i.unidadMedida, 
            i.cantidadInsumo, 
            COALESCE(p.nombrePresentacion, 'No asignado') AS nombrePresentacion, 
            COALESCE(pr.nombreProveedor, 'No asignado') AS nombreProveedor
        FROM insumos i
        LEFT JOIN presentacionesinsumos p ON i.idInsumo = p.idInsumoFK
        LEFT JOIN proveedoresinsumos pi ON p.idPresentacion = pi.idPresentacionFK
        LEFT JOIN proveedores pr ON pi.idProveedorFK = pr.idProveedor
    """)
    insumos = cur.fetchall()

    cur.close()

    return render_template('pages/admin/CRUD_Insumos.html', proveedores=proveedores, insumos=insumos)

# registar un insumo
@app.route("/register_insumo", methods=["POST"])
def register_insumo():
    if request.method == "POST":
        nombreInsumo = request.form["nombreInsumo"]
        unidadMedida = request.form["unidadMedida"]

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO insumos (nombreInsumo, unidadMedida, cantidadInsumo) VALUES (%s, %s, %s)",
            (nombreInsumo, unidadMedida, 0),  # cantidadInsumo = 0 por default :v - podemos eliminarlo de la bd pq es un campo calculado
        )
        mysql.connection.commit()
        cur.close()

        print("Insumo registrado")
        return redirect(url_for("CRUD_Insumos"))
    
@app.route("/get_insumo/<int:idInsumo>")
def get_insumo(idInsumo):
    cur = mysql.connection.cursor()
    cur.execute("SELECT idInsumo, nombreInsumo, unidadMedida FROM insumos WHERE idInsumo = %s", (idInsumo,))
    insumo = cur.fetchone()
    cur.close()

    if insumo:
        return {
            "idInsumo": insumo[0],
            "nombreInsumo": insumo[1],
            "unidadMedida": insumo[2],
        }
    else:
        return {"error": "Insumo no encontrado"}, 404
    

@app.route("/asignar_proveedor_presentacion", methods=["POST"])
def asignar_proveedor_presentacion():
    if request.method == "POST":
        idInsumo = request.form["idInsumo"]
        idProveedorFK = request.form["idProveedorFK"]
        precioProveedor = float(request.form["precioProveedor"])
        nombrePresentacion = request.form["nombrePresentacion"]
        cantidadBase = float(request.form["cantidadBase"])
        unidadBase = request.form["unidadMedidaAsignar"]

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO presentacionesinsumos (idInsumoFK, nombrePresentacion, cantidadBase, unidadBase) VALUES (%s, %s, %s, %s)",
            (idInsumo, nombrePresentacion, cantidadBase, unidadBase),
        )
        idPresentacion = cur.lastrowid

        cur.execute(
            "INSERT INTO proveedoresinsumos (idProveedorFK, idPresentacionFK, precioProveedor) VALUES (%s, %s, %s)",
            (idProveedorFK, idPresentacion, precioProveedor),
        )

        mysql.connection.commit()
        cur.close()

        print("Prov y presentacion asignados")
        return redirect(url_for("CRUD_Insumos"))