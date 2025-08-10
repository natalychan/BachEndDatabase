from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for school rankings lookups
rankings_api = Blueprint('rankings_api', __name__)

# ------------------------------------------------------------
# GET /api/rankings
# Purpose: List school rankings
@rankings_api.route('/rankings', methods=['GET'])
def list_rankings():
    query = "SELECT schoolName, ranking FROM school_rankings ORDER BY ranking DESC"
    current_app.logger.info("GET /rankings : listing")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /rankings : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response
