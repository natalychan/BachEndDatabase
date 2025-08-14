from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for clubs listing
club_members_api = Blueprint('club_members_api', __name__)

# GET /api/students/<student_id>/clubs
@club_members_api.route('/club_members', methods=['GET'])
def club_mems(studentId):
    query = """
        SELECT cm.clubName AS club_name
        FROM club_members cm
        WHERE cm.studentId = %s
    """
    cursor = db.get_db().cursor()
    cursor.execute(query, (studentId))
    theData = cursor.fetchall()
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response
