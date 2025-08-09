from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
advisors = Blueprint('advisors', __name__)

#------------------------------------------------------------
# Get all the club from the database, package them up,
# and return them to the client
@advisors.route('/advisors', methods=['GET'])
def get_advisor_email():
    query = '''
        SELECT u.emailAddress
        FROM advisors a
        JOIN users u ON a.userId = u.userId
        JOIN students s ON a.userId = s.advisor
    '''
    
   # logging the query for debugging purposes.  
    # The output will appear in the Docker logs output
    # This line has nothing to do with actually executing the query...
    # It is only for debugging purposes. 
    current_app.logger.info(f'GET /advisors query={query}')

    # get the database connection, execute the query, and 
    # fetch the results as a Python Dictionary
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    
    # Another example of logging for debugging purposes.
    # You can see if the data you're getting back is what you expect. 
    current_app.logger.info(f'GET /advisors Result of query = {theData}')
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response
    