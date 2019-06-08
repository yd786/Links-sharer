from functools import wraps
from flask import Flask, render_template, session, redirect, url_for, request
import random
import dns
from pymongo import MongoClient

app = Flask(__name__)


# local
# mclient = MongoClient("mongodb://127.0.0.1:27017")
# mdb = mclient["test"]["data"]

# remote
mclient = 
mdb = 

# custom decorators
def user_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "USER_ID" in session:
            return redirect(url_for('display_links'))
        return f(*args, **kwargs)
    return decorated_function


def check_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "USER_ID" in session:
            return f(*args, **kwargs)
        return redirect(url_for('display_links'))
    return decorated_function


# error page
@app.errorhandler(404)
def error_page(e):
    return render_template("404.html"), 404


# home
@app.route('/')
@user_logged_in
def index():
    return render_template("index.html")


# display data
@app.route("/display_links", methods=['POST', 'GET'])
def display_links():
    if "USER_ID" in session:
        data = mdb.find_one({"user_id":session["USER_ID"]})
        if data is None:
            session.pop("USER_ID")
            return redirect(url_for("index"))  # error message
        else:
            return render_template("display_links.html", data=data["links"])
    else:
        return redirect(url_for("index"))


# create user
@app.route("/send", methods=['POST', 'GET'])
def create_user():
    if request.method == "POST":
        if "USER_ID" in session:
            return redirect(url_for("display_links"))
        else:
            try:
                rnd = r()
                mdb.insert_one({"user_id":rnd,"links": []})
                session["USER_ID"] = rnd
                return redirect(url_for("display_links"))
            except Exception as e:
                return redirect(url_for('index'),error="Sorry, Please try again")
    else:
        return redirect(url_for('index'))


# display data using input
@app.route("/recieve", methods=["POST", "GET"])
def recieve():
    if request.method == "POST":
        data = mdb.find_one({"user_id":int(request.form["user_code"])})
        if data is not None:
            session["USER_ID"] = int(request.form["user_code"])
            return redirect(url_for("display_links"))
        else:
            flash("Sorry, No user exist for the specified code")
            return redirect(url_for('index'))  # error no user
    else:
        return render_template("index"), 404


# delete user
@app.route("/delete", methods=['POST', 'GET'])
@check_logged_in
def delete_user():
    if request.method == 'POST':
        mdb.delete_one({'user_id':session["USER_ID"]})
        session.pop("USER_ID")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


# routes related data editing -> add link routes
@app.route('/add_link/')
@check_logged_in
def add_link():
    title = request.args["ft_title"]
    href = request.args["ft_href"]
    link = {
        "title":title,
        "href": href
    }
    mdb.update_one({"user_id":session["USER_ID"]}, { "$push" : {"links" : link} })
    return redirect(url_for("display_links"))


@app.route('/update_link/')
@check_logged_in
def update_link():
    title = request.args["updatedTitle"]
    href = request.args["updatedHref"]
    key = request.args["key"]
    link = {
        "title":title,
        "href": href
    }
    mdb.update_one({"user_id": session["USER_ID"]},{"$pull":{"links":{'title':key}}})
    mdb.update_one({"user_id":session["USER_ID"]}, { "$push" : {"links" : link} })
    return redirect(url_for("display_links"))

@app.route('/delete_link/',methods=["POST","GET"])
@check_logged_in
def delete_link():
    if request.method == "POST":
        title = request.form["title"]
        mdb.update_one({"user_id": session["USER_ID"]},{"$pull":{"links":{'title':title}}})
        return redirect(url_for("display_links"))
    else:
        return redirect(url_for("index"))


# custom function
def r(r=0):
    for i in range(1, 7):
        r += (random.randint(0, 9) * pow(10, 6 - i))
    return r


# start website
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True , port=8000)
