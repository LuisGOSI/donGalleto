from flask import render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from db import app,mysql  
from werkzeug.security import generate_password_hash


@app.route("/registerCliente", methods=["POST"])
def register_cliente():
    if request.method == "POST":
        nombreCliente = request.form["nombreCliente"]
        telefono = request.form["telefono"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        
        cur = mysql.connection.cursor()
        
        try:
            cur.execute(
                "INSERT INTO clientes (nombreCliente, telefono) VALUES (%s, %s)",
                (nombreCliente, telefono)
            )
            idCliente = cur.lastrowid
            
            cur.execute(
                "INSERT INTO usuarios (email, password, rol, idClienteFK) VALUES (%s, %s, 'cliente', %s)",
                (email, password, idCliente)
            )
            
            mysql.connection.commit()
            flash("Cliente registrado exitosamente", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al registrar el cliente", "danger")
        finally:
            cur.close()
        
        return redirect(url_for("clientes"))
    
@app.route("/modifyCliente", methods=["POST"])
def modify_cliente():
    if request.method == "POST":
        idCliente = request.form["idCliente"]
        nombreCliente = request.form["Nombre"]
        telefono = request.form["Telefono"]
        email = request.form["Email"]
        
        cur = mysql.connection.cursor()
        
        try:
            cur.execute(
                "UPDATE clientes SET nombreCliente = %s, telefono = %s WHERE idCliente = %s",
                (nombreCliente, telefono, idCliente)
            )
            
            cur.execute(
                "UPDATE usuarios SET email = %s WHERE idClienteFK = %s",
                (email, idCliente)
            )
            
            mysql.connection.commit()
            flash("Cliente actualizado exitosamente", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al actualizar el cliente", "danger")
        finally:
            cur.close()
        
        return redirect(url_for("clientes"))
    
@app.route("/eliminarCliente", methods=["POST"])
def eliminar_cliente():
    if request.method == "POST":
        idCliente = request.form["idCliente"]
        
        cur = mysql.connection.cursor()
        
        try:
            cur.execute(
                "UPDATE usuarios SET status = 0 WHERE idClienteFK = %s",
                (idCliente,)
            )
            
            mysql.connection.commit()
            flash("Cliente desactivado exitosamente", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al desactivar el cliente", "danger")
        finally:
            cur.close()
        
        return redirect(url_for("clientes"))
    

@app.route("/get_cliente/<int:idCliente>")
def get_cliente(idCliente):
    cur = mysql.connection.cursor()
    
    cur.execute("""
        SELECT 
            c.idCliente,
            c.nombreCliente,
            c.telefono,
            u.email
        FROM 
            clientes c
        INNER JOIN 
            usuarios u ON c.idCliente = u.idClienteFK
        WHERE 
            c.idCliente = %s;
    """, (idCliente,))
    
    cliente = cur.fetchone()
    cur.close()
    
    if cliente:
        return {
            "idCliente": cliente[0],
            "nombreCliente": cliente[1],
            "telefono": cliente[2],
            "email": cliente[3]
        }
    else:
        return {"error": "Cliente no encontrado"}, 404
    
@app.route("/activarCliente", methods=["POST"])
def activar_cliente():
    if request.method == "POST":
        idCliente = request.form["idCliente"]
        
        cur = mysql.connection.cursor()
        
        try:
            cur.execute(
                "UPDATE usuarios SET status = 1 WHERE idClienteFK = %s",
                (idCliente,)
            )
            
            mysql.connection.commit()
            flash("Cliente activado exitosamente", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al activar el cliente", "danger")
        finally:
            cur.close()
        
        return redirect(url_for("clientes", status=0))