import hashlib
import sqlite3

from flask import Flask, render_template, g, request, flash, url_for, session
from werkzeug.utils import redirect

app = Flask(__name__)

app.secret_key = "pottery"

DATABASE = "database.db"

"""
#
# DATABASE
#
"""


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


"""
#
# ROUTES
#
"""


@app.route("/")
def root():
    cur = get_db().cursor()
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM items")
        item_data = cur.fetchall()
    conn.close()
    return render_template("index.html", title="Accueil", items=item_data, session=session)


@app.route("/login", methods=["POST", "GET"])
def login():
    if session.get("email") is not None:
        flash("Vous êtes déjà connecté")
        return redirect(url_for("root"))

    if "login" in request.form and "password" in request.form:
        with sqlite3.connect("database.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE email = ? AND password = ?",
                (
                    request.form["login"],
                    hashlib.sha256(request.form["password"].encode()).hexdigest(),
                ),
            )
            user = cur.fetchone()

            if user is None:
                flash("Mot de passe ou e-mail inconnus")
                return redirect("login")

            else:
                session["email"] = user[3]
                flash("Vous êtes connecté")
                return redirect(url_for("root"))

    else:
        return render_template("login.html", title="Connexion", session=session)


@app.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté")
    return redirect(url_for("root"))


@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("email") is not None:
        flash("Vous êtes déjà connecté")
        return redirect(url_for("root"))

    if (
            "login" in request.form
            and "password" in request.form
            and "password2" in request.form
    ):

        if request.form["password"] != request.form["password2"]:
            flash("Le mot de passe de confirmation n'est pas le même")
            return redirect(url_for("register"))

        with sqlite3.connect("database.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email = ?", (request.form["login"],))
            user = cur.fetchone()

            if user is not None:
                flash("Adresse email déjà utilisée")
                return redirect(url_for("register"))

            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (
                    request.form["login"],
                    hashlib.sha256(request.form["password"].encode()).hexdigest(),
                ),
            )
            flash("Bravo ! inscripton réussi ! vous pouvez désormais vous connectez")
            return redirect(url_for("login"))

    else:
        return render_template("register.html", title="S'inscrire", session=session)


if __name__ == "__main__":
    app.run(debug=True)
