import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})

# copy the database over
Base = automap_base()

# Using Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station




# Flask Setup

app = Flask(__name__)


# Flask Routes

@app.route("/")
def welcome():
    """List all api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;stop&gt;<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine) 
# Precipitation for the last 12 months 
    """Precipitation analysis in Hawaii over the last year"""
    results = session.query(measurement.date, func.avg(measurement.prcp))\
        .filter(measurement.date > '2016-08-22')\
        .group_by(measurement.date)\
        .order_by(measurement.date.desc())\
        .all()


    session.close()

    # Return the JSON representation of your dictionary.

    precipitation_results = []
    for date, prcp, in results:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict ["date"]= date
        precipitation_results.append(precipitation_dict)


    return jsonify(precipitation_results)

    # Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    # create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of all the active Weather stations in Hawaii"""
    station_query = session.query(station.station).all()
    
    session.close()

    station_results = list(np.ravel(station_query))
    return jsonify (stations=station_results)


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    #last_date
    recent_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
    recent_date = recent_date[0]
    latest_date=dt.datetime.strptime(recent_date,"%Y-%m-%d")
    last_date=latest_date-dt.timedelta(days=365)

    #results
    # Query all date and tobs values
    
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= last_date).\
        filter(measurement.station == 'USC00519281').all()

    session.close()

    tobs_data = []
    for date, tobs in results:
            tobs_dict = {}
            tobs_dict[date] = tobs
            tobs_data.append(tobs_dict)
    

    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def chicken_nugget(start=None,end=None):
     session = Session(engine)
     sel=[func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)]

     if not end:
          
        start=dt.datetime.strptime(start,"%Y-%m-%d")
        results=session.query(*sel).filter(measurement.date>=start).all()

        session.close()

        answer=list(np.ravel(results))
        return jsonify(temps=answer)
     


     start=dt.datetime.strptime(start,"%Y-%m-%d")
     end=dt.datetime.strptime(end,"%Y-%m-%d")
     results=session.query(*sel).filter(measurement.date>=start).filter(measurement.date<=end).all()

     session.close()

     answer=list(np.ravel(results))
     return jsonify(temps=answer)









     return ("tada")



if __name__ == "__main__":
     app.run(debug=True)






    

