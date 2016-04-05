import datetime
import io, csv
import AdminTools
from flask import Flask, render_template, request, make_response
app = Flask(__name__)


@app.route('/routing', methods=['GET', 'POST'])
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
def return_dbtools_page():
	if request.method == 'POST':
		return "NOT YET!"
	else:
		return render_template('dbtools.html', name=None)

@app.route('/updatemidmonth', methods=['GET'])
def update_mid_month():
	AdminTools.update_mid_month()
	return "Done updateing mid month from Walden and WorkWave"

if __name__ == '__main__':
	app.debug = True
	app.run()


