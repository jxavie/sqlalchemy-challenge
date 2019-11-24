# Import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# conn = engine.connect()

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the database
    # session = Session(bind=engine)
    session = Session(engine)

    # Query precipitation records for latest year-long period available
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    
    # Initiate list to hold query results
    rain_list = []

    # Use a for loop to assign data and prcp measurement data pairs into a dictionary,
    # and append each dictionary as an entry into a list.
    for date, prcp in results:
        rain_dict = {}
        rain_dict['date'] = date
        rain_dict['prcp'] = prcp
        rain_list.append(rain_dict)
    
    return jsonify(rain_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the database
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into a normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create session (link) from Python to the database
    session = Session(engine)
        
    # Query precipitation records for latest year-long period available
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    end_date = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    start_date = dt.datetime.strftime(end_date - dt.timedelta(days=365),'%Y-%m-%d')
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(func.strftime('%Y-%m-%d', Measurement.date) >= start_date).all()

    session.close()

    # Initiate list to hold query results
    temp_list = []

    # Use a for loop to assign data and prcp measurement data pairs into a dictionary,
    # and append each dictionary as an entry into a list.
    for date, tobs in results:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['tobs'] = tobs
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start_date>")
def temp_start_only(start_date):
    
    # Create session (link) from Python to the database
    session = Session(engine)

    # Query latest and earliest date available in dataset
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    earliest_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()[0]

    # Query the minimum, average, and maximum temperatures in the period between the start date specified
    # and latest date available if start date specified is between the earliest and latest dates available
    if (latest_date >= start_date): #and (start_date >= earliest_date):
        t_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()[0][0]
        t_ave = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()[0][0]
        t_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()[0][0]

        temp_dict ={}
        temp_dict['min temp'] = t_min
        temp_dict['average temp'] = t_ave
        temp_dict['max temp'] = t_max
        temp_list = [temp_dict]
    
    session.close()

    if (latest_date >= start_date) and (start_date >= earliest_date):
        return jsonify(temp_list)
    
    # elif (start_date < earliest_date):
    #     return jsonify({"Error": f"Start date specified earlier than dates availabe in data set. Earliest date available: {earliest_date}"}), 404

    # else:
    #     return jsonify({"Error": f"Start date specified earlier than dates availabe in data set. Latest date available: {latest_date}"}), 404

    else:
        return jsonify({"Error": f"Start date specified outside available dates in dataset. Choose a date between {earliest_date} and {latest_date}"}), 404

@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_start_end(start_date, end_date):
    
    # Create session (link) from Python to the database
    session = Session(engine)

    # Query latest and earliest date available in dataset
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    earliest_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()[0]

    # Query the minimum, average, and maximum temperatures in the period between the start date specified
    # and latest date available if start date specified is between the earliest and latest dates available
    if (start_date >= earliest_date) and (end_date <= latest_date):
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
            .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

        t_min = results[0][0]
        t_ave = results[0][1]
        t_max = results[0][2]

        temp_dict ={}
        temp_dict['min temp'] = t_min
        temp_dict['average temp'] = t_ave
        temp_dict['max temp'] = t_max
        temp_list = [temp_dict]
    
    session.close()

    if (start_date >= earliest_date) and (end_date <= latest_date):
        return jsonify(temp_list)

    else:
        return jsonify({"Error": f"Specified dates outside available dates in dataset. Choose a date between {earliest_date} and {latest_date}"}), 404

if __name__ == '__main__':
    app.run(debug=True)
