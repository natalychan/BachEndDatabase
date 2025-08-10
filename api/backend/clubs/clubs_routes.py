from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for clubs listing
clubs_api = Blueprint('clubs_api', __name__)

# ------------------------------------------------------------
# GET /api/clubs
# Purpose: List all clubs
@clubs_api.route('/clubs', methods=['GET'])
def list_clubs():
    query = "SELECT name AS club_name FROM clubs ORDER BY name"
    current_app.logger.info("GET /clubs : listing clubs")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /clubs : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response