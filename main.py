from flask import request, render_template, url_for, redirect, session
from app import create_app
from app.migrate import init_db
from app.models import db, User

app = create_app()


@app.route("/")
def home():
    if not session:
        return redirect(url_for("signin"))
    users = User.query.all()
    ctx = {
        "title": "Inicio",
        "users": users
    }
    return render_template("index.html", **ctx)


@app.errorhandler(404)
def notFound(error):
    ctx = {
        "title": "Pagina no encontrada",
        "error": error
    }
    return render_template("notFound.html", **ctx)


@app.route("/auth/signin", methods=["GET", "POST"])
def signin():
    if session:
        return redirect(url_for("home"))
    ctx = {
        "title": "Ingresar",
    }
    if request.method == "POST":
        try:
            email = request.form["email"]
            password = request.form["password"]
            if email != "" and password != "":
                user = User.query.filter_by(email=email).first()
                print(user)
                if not user:
                    ctx["error"] = "Usuario o contraseña incorrecta"
                    return render_template("signin.html", **ctx)
                if user.check_password(password):
                    session["username"] = user.username
                    session["email"] = user.email
                    return redirect(url_for("home"))
                ctx["error"] = "Usuario o contraseña incorrecta"
        except:
            ctx["error"] = "Fallo en el servidor"
    return render_template("signin.html", **ctx)


@app.route("/auth/signup", methods=["GET", "POST"])
def signup():
    if session:
        return redirect(url_for("home"))
    ctx = {
        "title": "Registrarse",
    }
    if request.method == "POST":
        try:
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            if username != "" and email != "" and password != "":
                newUser = User(username=username, email=email)
                newUser.set_password(password)
                db.session.add(newUser)
                db.session.commit()
                return redirect(url_for("home"))
            ctx["error"] = "Ingrese todos los datos correctamente"
        except:
            ctx["error"] = "Fallo en el servidor"
    return render_template("signup.html", **ctx)


@app.route("/auth/logout")
def logout():
    session.pop('username', default=None)
    session.pop('email', default=None)
    return redirect(url_for('signin'))


@app.route("/database")
def database():
    init_db()
    return "Database created"
