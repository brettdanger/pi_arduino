from flask import Flask, Response, g, render_template
import sqlite3
import json
import time


app = Flask(__name__)

app.config.update(
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True
)

DATABASE = '../tempature.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def get_current_temp():

    cur = get_db().cursor()
    cur.execute("select * from tempature_log order by timestamp desc limit 1")

    rows = cur.fetchall()

    for row in rows:
    	timestamp = row[0] - (60*60*6)
        temp = row[2]
    
    return temp


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET'])
def get_index():
	return render_template('index.html', current_temp = get_current_temp())


@app.route('/get_temps', methods=['GET'])
def get_temp_json():

	return_array = []

	time_range = int(time.time()) - (60*60*24.0)
	cur = get_db().cursor()
    	cur.execute("SELECT * FROM tempature_log WHERE timestamp > ?", (time_range, ))

    	rows = cur.fetchall()

    	for row in rows:
		timestamp = row[0] - (60*60*6)
        	temp = row[2]
		return_array.append({'x': timestamp, 'y': temp})

	response = Response(json.dumps(return_array))
	return response
	

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
