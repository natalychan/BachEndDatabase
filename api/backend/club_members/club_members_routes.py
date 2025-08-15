from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for clubs listing
club_members_api = Blueprint('club_members_api', __name__)

# GET /api/students/<student_id>/clubs
@club_members_api.route('/club_members/<int:studentId>/clubs', methods=['GET'])
def club_mems(studentId):
    query = """
        SELECT clubName 
        FROM club_members cm 
        join clubs c 
            on cm.clubName = c.name
        join students s 
            on cm.studentId = s.userId
        WHERE s.userId = %s
    """
    current_app.logger.info("GET /club_members/%s/clubs", studentId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (studentId,))
    theData = cursor.fetchall()
    theDataDict = [{"Club Name": row[0]} for row in theData]
    current_app.logger.info("GET /club_members/%s/clubs : rows=%d", studentId, len(theData))
    response = make_response(jsonify(theDataDict))
    response.status_code = 200
    return response