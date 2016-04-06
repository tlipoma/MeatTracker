import datetime
import io, csv
import AdminTools
from flask import Flask, render_template, request, make_response, session, flash, redirect, url_for
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin,
                            confirm_login, fresh_login_required)

app = Flask(__name__)

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        return self.active

USERS = {
    1: User(u"Notch", 1),
    2: User(u"Steve", 2),
    3: User(u"Creeper", 3, False),
}

USER_NAMES = dict((u.name, u) for u in USERS.itervalues())

SECRET_KEY = "yeah, not actually a secret"
DEBUG = True

app.config.from_object(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(id):
    return USERS.get(int(id))

login_manager.setup_app(app)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        if username in USER_NAMES:
            remember = request.form.get("remember", "no") == "yes"
            if login_user(USER_NAMES[username], remember=remember):
                flash("Logged in!")
                return redirect(request.args.get("next") or url_for("return_dbtools_page"))
            else:
                return "Sorry, but you could not log in."
        else:
            return "Invalid username"
    return render_template("login.html")


@app.route('/routing', methods=['GET', 'POST'])
@login_required
def return_routing_page():
	# For now go to routing
	if request.method == 'POST':
		try:
			day = int(request.form['element_1_2'])
			month = int(request.form['element_1_1'])
			year = int(request.form['element_1_3'])
			get_day = datetime.datetime(year, month, day)
			# Build CSV
			csv_array = AdminTools.build_route_csv(get_day)
			csv_string = ""
			if csv_array != None:
				for line in csv_array:
					csv_string += line
				output = make_response(csv_string)
				output.headers["Content-Disposition"] = "attachment; filename=export.csv"
				output.headers["Content-type"] = "text/csv"
				return output
			else:
				return "Error, probably in ww/network"
		except:
			return "ERROR"
			return "running"
	else:
		return render_template('routing.html', name=None)

@app.route('/dbtools', methods=['GET', 'POST'])
@login_required
def return_dbtools_page():
	if request.method == 'POST':
		return "NOT YET!"
	else:
		return render_template('dbtools.html', name=None)

@app.route('/updatemidmonth', methods=['GET'])
@login_required
def update_mid_month():
	AdminTools.update_mid_month()
	return "Done updateing mid month from Walden and WorkWave"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == '__main__':
	app.config["SECRET_KEY"] = "ITSASECRET"
	app.debug = True
	app.run()


