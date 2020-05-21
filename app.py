# 2)    SETTING UP THE CLIMATE APP

##############################################################################
''' DEPENDENCIES '''
##############################################################################
import pandas as pd
import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

##############################################################################
''' DATABASE SETUP - CREATE ENGINE; AUTOMAP; REFLECTION '''
##############################################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base= automap_base()
Base.prepare(engine, reflect = True)

##############################################################################
''' Save references to each table
    Assign the measurement class to a variable called `Measurement`
    Assign the station class to a variable called `Station`'''
##############################################################################

Measurement = Base.classes.measurement
Station = Base.classes.station

##############################################################################
''' FLASK SETUP - CREATE APP; PASS-IN __NAME__ '''
##############################################################################

app = Flask(__name__)

##############################################################################
''' FLASK ROUTES - WELCOME; PRECIP; STATIONS; TOBS; START_DATE; START_END '''
##############################################################################

@app.route("/")
def welcome():
    return(
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start <br/>"
        f"/api/v1.0/start/end <br/>" 
        f"For /api/v1.0/start route, specify a starting date in this range: 2016-08-23 - 2017-08-23 <br/>"
        f"For /api/v1.0/start/end route, specify a starting AND an ending date in this range: 2016-08-23 - 2017-08-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #  Create session and bind to engine
    session = Session(engine)
    
    #   Query all precipitations (data and measurement) from one year ago
    #   and close session
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days = 365)
    one_year_ago

    #   Run a query to retrieve the data and precip scores
    precip = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= one_year_ago).all()
    session.close()

    #   np.ravel to create a dictionary of the results
    #   Add "list()" to enable jsonification
    precip_list = list(np.ravel(precip))
    
    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    #   Create session and bind to engine
    session = Session(engine)

    #   Query all stations and close session
    stations = session.query(Station.station).all()
    session.close()

    #   np.ravel to create a dictionary of the results
    #   Add "list()" to enable jsonification
    stations_list = list(np.ravel(stations))
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #   Create session and bind to engine
    session = Session(engine)

    #   Query the date and temperature observations of the most active station
    #   for the last year of data
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days = 365)
    
    #   Determine most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()

    most_active_station = active_stations[0][0]

    #   Determine tobs for most_active_station and close session
    tobs = session.query(Measurement.date, Measurement.tobs).\
          filter(Measurement.date >= one_year_ago).\
          filter(Measurement.station == most_active_station).all()

    session.close()

    #   np.ravel to create a dictionary of the results
    #   Add "list()" to enable jsonification 
    tobs_list = list(np.ravel(tobs))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    #   Create session and bind to engine
    session = Session(engine)

    #   Query min, avg, and max for all dates greater than or equal to the
    #   start date; Close session
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    temperatures = session.query(*sel).\
            filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    session.close()

    #   np.ravel to create a dictionary of the results
    #   Add "list()" to enable jsonification
    temperatures_list = list(np.ravel(temperatures))

    return jsonify(temperatures_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    #   Create session and bind to engine
    session = Session(engine)

    #   Query min, avg, and max for all dates greater than or equal to the
    #   start date; Close session
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    temperatures = session.query(*sel).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    session.close()

    #   np.ravel to create a dictionary of the results
    #   Add "list()" to enable jsonification
    temperatures_list = list(np.ravel(temperatures))

    return jsonify(temperatures_list)


if __name__ == "__main__":
    app.run(debug = True)
