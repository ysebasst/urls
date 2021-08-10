from flask import request, render_template, url_for, redirect, session, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from flask_pymongo import PyMongo, ObjectId
from bson import json_util

app = create_app()
mongo = PyMongo(app)
db = mongo.db


def normalizeData(data):
    data_str = json_util.dumps(data)
    newData = json_util.loads(data_str)
    for element in newData:
        element["_id"] = str(element["_id"])
    return newData


@app.route("/")
def home():
    if not session:
        return redirect(url_for("signin"))
    users_db = db.users.find()
    users = normalizeData(users_db)
    urls_db = db.urls.find({"user_id": session["user_id"]})
    urls = normalizeData(urls_db)
    ctx = {
        "title": "Inicio",
        "users": users,
        "urls": urls
    }
    return render_template("index.html", **ctx)


@app.route("/urls", methods=["POST"])
def createUrl():
    title = request.json["title"]
    url = request.json["url"]
    if title and url:
        id = db.urls.insert({
            "title": title,
            "url": url,
            "user_id": session["user_id"]
        })
        response = json_util.dumps({"data": {
            "_id": str(id),
            "title": title,
            "url": url,
            "user_id": session["user_id"]
        }, "error": False})
    else:
        response = json_util.dumps(
            {"data": False, "error": "Rellene todos los campos"})

    return Response(response, mimetype="application/json")


@app.route("/urls/<id>", methods=["DELETE"])
def deleteUrl(id):
    urlDelete = db.urls.delete_one({
        "_id": ObjectId(id),
        "user_id": session["user_id"]
    })
    print(urlDelete.raw_result)
    if urlDelete.raw_result["n"] > 0:
        response = json_util.dumps({"error": False})
    else:
        response = json_util.dumps({"error": "access denied"})
    return Response(response, mimetype="application/json")


@ app.errorhandler(404)
def notFound(error=None):
    ctx = {
        "title": "Pagina no encontrada",
        "error": error
    }
    return render_template("notFound.html", **ctx)


@ app.route("/auth/signin", methods=["GET", "POST"])
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
            if email and password:
                user = db.users.find_one({"email": email})
                print(user)
                if user:
                    if check_password_hash(user["password"], password):
                        session["user_id"] = str(user["_id"])
                        session["email"] = email
                        session["username"] = user["username"]
                        return redirect(url_for("home"))
                    else:
                        ctx["error"] = "Usuario o contraseña incorrecta"
                else:
                    ctx["error"] = "Usuario o contraseña incorrecta"
            else:
                ctx["error"] = "Rellene todos los campos"
        except:
            ctx["error"] = "Fallo en el servidor"
    return render_template("signin.html", **ctx)


@ app.route("/auth/signup", methods=["GET", "POST"])
def signup():
    if session:
        return redirect(url_for("home"))
    ctx = {
        "title": "Registrarse",
    }
    if request.method == "POST":
        try:
            username = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            if username and email and password:
                userExist = db.users.find_one({"email": email})
                if userExist:
                    ctx["error"] = "Error: Usuario ya creado"
                else:
                    id = db.users.insert({
                        "email": email,
                        "password": generate_password_hash(password),
                        "username": username
                    })
                    session["user_id"] = str(id)
                    session["email"] = email
                    session["username"] = username
                    return redirect(url_for("home"))
            else:
                ctx["error"] = "Ingrese todos los datos correctamente"
        except:
            ctx["error"] = "Fallo en el servidor"
    return render_template("signup.html", **ctx)


@ app.route("/auth/logout")
def logout():
    session.pop('user_id', default=None)
    session.pop('username', default=None)
    session.pop('email', default=None)
    return redirect(url_for('signin'))
