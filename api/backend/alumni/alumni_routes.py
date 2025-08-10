########################################################
# Sample customers blueprint of endpoints
# Remove this file if you are not using it in your project
########################################################

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
alumni = Blueprint('alumni_api', __name__)

#------------------------------------------------------------
# Get all the students from the database, package them up,
# and return them to the client
@alumni.route('/alumni', methods=['GET'])
def get_students():
    query = '''
        SELECT s.college, 
            COUNT(*) AS total_alumni, 
            SUM(a.hasJob = 'true') AS employed_alumni,
            ROUND(SUM(a.hasJob = 'true') * 1.0 / COUNT(*), 2) AS employment_rate
        FROM alumni AS a
            JOIN students AS s ON a.studentId = s.userId
        GROUP BY s.college
        ORDER BY employment_rate DESC;
      
    '''
    # logging the query for debugging purposes.  
    # The output will appear in the Docker logs output
    # This line has nothing to do with actually executing the query...
    # It is only for debugging purposes. 
    current_app.logger.info(f'GET /alumni query={query}')

    # get a cursor object from the database
    cursor = db.get_db().cursor()

    # use cursor to query the database for a list of products
    cursor.execute(query)

    # fetch all the data from the cursor
    # The cursor will return the data as a 
    # Python Dictionary
    theData = cursor.fetchall()

    # Another example of logging for debugging purposes.
    # You can see if the data you're getting back is what you expect. 
    current_app.logger.info(f'GET /alumni/<userId> Result of query = {theData}')

    # Create a HTTP Response object and add results of the query to it
    # after "jasonify"-ing it.
    response = make_response(jsonify(theData))
    # set the proper HTTP Status code of 200 (meaning all good)
    response.status_code = 200
    # send the response back to the client
    return response