# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Transforming existing database

Base = automap_base()

# reflecting the tables

Base.prepare(autoload_with = engine, reflect = True)

# Storing references to each table

station = Base.classes.station
measurement = Base.classes.measurement

# Linking Python to the DataBase

session = Session(engine)
   

#################################################
# Flask Setup
#################################################

app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>" )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data"""
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Execute a query to fetch both the data and precipitation scores, and arrange the results in chronological order based on the date.
    
    precipitation = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= prev_year).all()
   
    session.close()
    # Creating a new dictionary where date is the key and prcp is the value
    
    #jsonify dictionary 
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)
       


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""

    # retrieve all 9 stations
    stations_query = session.query(station.station).all()
    
    session.close()

    # open the tuples to return a list
    stations = list(np.ravel(stations_query))

    #jsonify list
    return jsonify(stations = stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures of the most active station in the last year"""

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= prev_year).all()
    session.close()
    temps = list(np.ravel(results))
    # Return the results
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(measurement.date >= start).all()
        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps)
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)
