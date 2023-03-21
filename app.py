import os
from flask import Flask
from flask import render_template, request,redirect,session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory #obtener informacion directamente de la imagen

app=Flask(__name__) ## creamos el servidor

app.secret_key="devolteca"
##guardamos la funcion en una variable
mysql=MySQL()
##ingresamos las credenciales
app.config["MYSQL_DATABASE_HOST"]="localhost"
app.config["MYSQL_DATABASE_USER"]="root"
app.config["MYSQL_DATABASE_PASSWORD"]="123"
app.config["MYSQL_DATABASE_DB"]="sitio"
##iniciamos la conexion con la base de datos
mysql.init_app(app)

## creamos la ruta de inicio, la que corresponde a index.html
@app.route("/") 

def inicio():
## render_template nos va a mostrar lo que tenemos en index.html en la ruta especifiacada arriba
        return render_template("sitio/index.html") 

@app.route("/img/<imagen>")
def imagenes(imagen):
        print(imagen)
        return send_from_directory(os.path.join("templates/sitio/img"),imagen)


@app.route("/css/<archivocss>")
def css_link(archivocss):
        return send_from_directory(os.path.join("templates/sitio/css"),archivocss)


@app.route("/libros")
def libros():

        conexion=mysql.connect()
        cursor=conexion.cursor()
        cursor.execute("SELECT * FROM `libros`")
        libros=cursor.fetchall()
        conexion.commit()
        ##almacenamos los libros en la variable libros y se lo pasamos por parametro para mostrarlo en el front
        
        return render_template("sitio/libros.html",libros=libros)


@app.route("/nosotros")
def nosotros():
        return render_template("sitio/nosotros.html")


@app.route("/admin")
def admin_index():
        if not "login" in session:
                return redirect("/admin/login")
        return render_template("admin/index.html")

@app.route("/admin/login")
def admin_login():
        return render_template("admin/login.html")
@app.route("/admin/login",methods=["POST"])
def admin_login_post():

        _usuario=request.form["txtUsuario"]
        _password=request.form["txtContraseña"]


        if _usuario == "admin" and _password=="123":
                session["login"]=True
                session["usuario"] ="Administrador"
                return redirect("/admin")        
        
        return render_template("admin/login.html", mensaje="Acceso denegado")

@app.route("/admin/cerrar")
def admin_login_cerrar():
        session.clear()
        return redirect("/admin/login")


@app.route("/admin/libros")
def admin_libros():
        if not "login" in session:
                return redirect("/admin/login")
        conexion=mysql.connect()
        cursor= conexion.cursor()
        cursor.execute("SELECT * FROM `libros`")
        ## guardamos todo los elementos de la tabla "libros" en una variable con fetchall
        libros=cursor.fetchall()
        conexion.commit()
        # print(libros)
        
        
        return render_template("admin/libros.html",libros=libros)


##recepcionamos los datos atraves del metodo post
@app.route("/admin/libros/guardar",methods=["POST"]) 


def admin_libros_guardar():
        if not "login" in session:
                return redirect("/admin/login")
##Guardamos en una variable lo que este adentro del formulario con el metodo post
        _nombre=request.form["txtNombre"]
        _url=request.form["txtURL"]
        _archivo=request.files["txtImagen"]
        
        tiempo=datetime.now()
        horaActual=tiempo.strftime("%Y%H%M%S")
        if _archivo.filename!="":
                nuevoNombre=horaActual+"_"+_archivo.filename
                _archivo.save("templates/sitio/img/"+nuevoNombre )

        
        ##conectamos esta ruta a la base de datos
        conexion=mysql.connect()
        sql="INSERT INTO `libros` (`id`,`nombre`, `imagen`, `url`) VALUES ('NULL',%s, %s, %s);"
        datos=(_nombre,nuevoNombre,_url)
        ##abrimos la conexion con la bd
        conexion=mysql.connect()
        ##se genera un curssor
        cursor=conexion.cursor()
        ##el cursor ejecuta la query
        cursor.execute(sql,datos)
        ##mandamos esta conexion
        conexion.commit()


         # print(_nombre)
        # print(_url)
        # print(_archivo) 
        return redirect("/admin/libros")


@app.route("/admin/libros/borrar", methods=["POST"])
def admin_libros_borrar():
        if not "login" in session:
                return redirect("/admin/login") 
        _id=request.form["txtID"]
        conexion=mysql.connect()
        cursor=conexion.cursor()
        cursor.execute("SELECT imagen FROM `libros` WHERE id = %s",(_id))
        libros=cursor.fetchall()
        conexion.commit()
        
        if os.path.exists("templates/sitio/img/" + str(libros[0][0])):
                os.unlink("templates/sitio/img/" + str(libros[0][0]))
        
        
        conexion=mysql.connect()
        cursor=conexion.cursor()
        cursor.execute("DELETE FROM `libros` WHERE `libros`.`id` = %s",(_id))
        conexion.commit()
        return redirect("/admin/libros")




if __name__== "__main__":
        app.run(debug=True)
