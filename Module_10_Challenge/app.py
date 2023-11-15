# Import the dependencies.
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify 

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Start at the homepage, list all the available routes.
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitation_results = session.query(measurement.prcp, measurement.date).all()
    precipitaton_values = []
    for prcp, date in precipitation_results:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict["date"] = date
        precipitaton_values.append(precipitation_dict)
    # Return the JSON representation of your dictionary.
    return jsonify(precipitaton_values)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_results = session.query(Station.station, Station.id).all()
    stations_values = []
    for station, id in stations_results:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['id'] = id
        stations_values.append(stations_dict)
    return jsonify (stations_values)

# Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs") 
def tobs():
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
        order_by(func.count(measurement.station).desc()).\
        group_by(measurement.station)
    most_active_station = active_stations.first()
    active_station_id = most_active_station[0]
    recent_date_active = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == active_station_id).\
        order_by(measurement.date.desc()).first()
    recent_date_active = recent_date_active[0]
    # Most recent date is 2017-08-18
    start_date_active = '2016-08-18'
    tobs_results = session.query(measurement.date, measurement.tobs, measurement.station).\
        filter(measurement.date >= start_date_active).\
        filter(measurement.station == active_station_id)
    tobs_values = []
    for date, tobs, station in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_dict["station"] = station
        tobs_values.append(tobs_dict)
    return jsonify(tobs_values)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start range.
@app.route("/api/v1.0/<start>")
def start_date(start):
    start_date_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start)
    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    return jsonify(start_date_tobs_values)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    end_date_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    end_tobs_date_values = []
    for min, avg, max in end_date_tobs_results:
        end_tobs_date_dict = {}
        end_tobs_date_dict["min_temp"] = min
        end_tobs_date_dict["avg_temp"] = avg
        end_tobs_date_dict["max_temp"] = max
        end_tobs_date_values.append(end_tobs_date_dict) 
    return jsonify(end_tobs_date_values)

# Allow running from command line with python app.py
if __name__ == "__main__":
    app.run(debug=True)
