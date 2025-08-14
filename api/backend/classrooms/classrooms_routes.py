from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
classrooms_api = Blueprint('classrooms_api', __name__)

#------------------------------------------------------------
# GET /api/classrooms
# Purpose: List all classrooms that were not maintained in the last 2 months
@classrooms_api.route('/classrooms', methods=['GET'])
def list_classrooms():  # Fixed function name
    query = '''
        SELECT lastMaintained, roomNumber
        FROM classrooms
        WHERE lastMaintained < DATE_SUB(NOW(), INTERVAL 2 MONTH)
        ORDER BY lastMaintained;     
    '''
    current_app.logger.info(f'GET /classrooms query={query}')
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info(f'GET /classrooms Result of query = {theData}')  # Fixed logging
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

