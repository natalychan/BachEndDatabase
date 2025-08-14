from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for clubs listing
club_members_api = Blueprint('club_members_api', __name__)

# GET /api/students/<student_id>/clubs
@club_members_api.route('/club_members/<int:studentId>', methods=['GET'])
def club_mems(studentId):
    query = """
        SELECT cm.clubName AS club_name
        FROM club_members cm
        WHERE cm.studentId = %s
    """
    current_app.logger.info("GET /club_members/%s", studentId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (studentId,))
    theData = cursor.fetchall()
    theDataDict = [{"Club Name": row[0]} for row in theData]
    current_app.logger.info("GET /club_members/%s : rows=%d", studentId, len(theData))
    response = make_response(jsonify(theDataDict))
    response.status_code = 200
    return response