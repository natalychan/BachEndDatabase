from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for clubs listing
clubs_api = Blueprint('clubs_api', __name__)

# GET /api/students/<student_id>/clubs
@clubs_api.route('/club_members', methods=['GET'])
def club_mems(userId):
    query = """
        SELECT cm.clubName AS club_name
        FROM club_members cm
        WHERE cm.userId = %s
    """
    cursor = db.get_db().cursor()
    cursor.execute(query, (userId))
    theData = cursor.fetchall()
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response
