# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

app = Flask(__name__)
#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table (we know the table names based on the jupyter hawaii_climate_tracking notebook)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

#the homepage for the website I created (defined in function home) is
#localhost:5000


#################################################
# Flask Routes
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Weather Local API!<br><br>"
        f"Here are the available routes: <br>"
        f"localhost:5000/api/v1.0/precipitation <br>"
        f"localhost:5000/api/v1.0/stations <br>"
        f"localhost:5000/api/v1.0/tobs <br>"
        f"localhost:5000/api/v1.0/start <br>"
        f"localhost:5000/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    oneYearAgo = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the date and precipitation values
    last12months = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= oneYearAgo).all()
    session.close()

    #saving the precipitation data as a dictionary, using date as the key and prcp as the value
    precipitation_dictionary = {date: prcp for date, prcp in last12months} 
    return jsonify(precipitation_dictionary) #turning the resulting dictionary into a json
#the page should display a dictionary showing every date between 8/23/2016 and 8/23/2017 and the corresponding precipitation measurement for each date.



@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(Station.station).all() #Return the stations from the dataset (pulling from Station table, so no need to group)
    session.close()
    stationList = list(np.ravel(station_list)) #convert results into a list using numpy.ravel
    return jsonify(stationList) #jsonify the list
#the page should display a list of the stations by name.


@app.route("/api/v1.0/tobs")
def temps():
    #Calculate the date one year from the last date in the dataset.
    oneYearAgo = dt.date(2017, 8, 23) - dt.timedelta(days=365) 
    #Perform a query to retrieve the dates and temperature values for the most active plant for the last year of data.
    temp_records = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= oneYearAgo).filter(Measurement.station == 'USC00519281').all()

    session.close()
    temperatureRecords = list(np.ravel(temp_records)) #convert results into a list using numpy.ravel
    return jsonify(temperatureRecords) #jsonify the list
#the page should display a list containing the dates and temperatures logged at the most active plant (USC00519281) on that date for the previous year of data. 
#Each date in the list is followed by the temperature logged on that date 
# i.e., if row 0 lists '2016-08-23' and row 1 lists '77.0', that means the temperature logged at the most active plant on 8/23/2016 was 77 degrees.


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):
    stats = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)] #calculating the min, max, and avg using the respective func functions.

    if not end:
        startDate = dt.datetime.strptime(start,"%m%d%Y")
        results = session.query(*stats).filter(Measurement.date >= startDate).all()
        session.close()
        tempList = list(np.ravel(results))
        return jsonify(tempList)
    #if no end date is given, the resulting list contains min, max and avg temperatures from the 'start' date up to the most recent date in the data set.

    else:
        startDate = dt.datetime.strptime(start,"%m%d%Y")
        endDate = dt.datetime.strptime(end,"%m%d%Y")
        results = session.query(*stats).filter(Measurement.date >= startDate).filter(Measurement.date <= endDate).all()
        session.close()
        tempList = list(np.ravel(results))
        return jsonify(tempList)
    #if an end date is given, the resulting list contains min, max, and avg temperatures from the 'start' date up to and including the 'end' date.
    
#################################################
if __name__ == '__main__':
    app.run(debug=True)
#other half of the Flask program