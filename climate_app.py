#Import Deliverables
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

##########################################
#Database Setup
##########################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Base.classes.keys()

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to Surf's Up!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/2017-01-01<br/>"
        f"/api/v1.0/2017-01-01/2017-01-14<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return a JSON representation of a dictionary with the date and precipitation value"""

    one_year_diff=dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=one_year_diff).all()

#create dictionary for precipitation  
    prcp_dict={}
    for rain in precipitation:
        prcp_dict[rain[0]]=precipitation[1]
    
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""

    results=session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

#create list of dictionaries (one for each observation)
    stations_list = []
    for station in results:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)
    
@app.route("/api/v1.0/temperature")
def temperature():

    """Return a JSON list of temperature observations for the previous year."""

    temperatures= session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>='2016-08-023').filter(Measurement.station=='USC00519281').all()

#create list of dictionaries (one for each observation)
    temp_list = []
    for temperature in temperatures:
        temp_dict = {}
        temp_dict["date"] = temperature.date
        temp_dict["tobs"] = temperature.tobs
        temp_list.append(temp_dict)

    return jsonify(temp_list)


@app.route("/api/v1.0/<start>")
def start(start=None):

    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()

#create list of dictionaries (one for each observation)   
    start_list=[]

    for dates in start_date:
       date_dict={}
       date_dict["Date"]=dates[0]
       date_dict["Low Temperature"]=dates[1]
       date_dict["Avg Temperature"]=dates[2]
       date_dict["High Temperature"]=dates[3]
       start_list.append(date_dict) 
   
    return jsonify(start_list)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    first_last = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
#create list of dictionaries (one for each observation)
#     
    dates_list=[]
    for startend in first_last:
        dates_dict={}
        dates_dict["Date"]= startend[0]
        dates_dict["Low Temperature"]= startend[1]
        dates_dict["Avg Temperature"]= startend[2]
        dates_dict["High Temperature"]= startend[3]
        dates_list.append(dates_dict)

    return jsonify(dates_list)

if __name__ == '__main__':
        app.run(debug=True)