from flask import Blueprint, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for clubs listing
club_members_api = Blueprint('club_members_api', __name__)

# GET /api/students/<student_id>/clubs
@club_members_api.route('/club_members/<int:studentId>/clubs', methods=['GET'])
def club_mems(studentId):
    """
    Returns all clubs for a given studentId.
    """
    query = "SELECT clubName FROM club_members WHERE studentId = %s"
    
    try:
        cursor = db.get_db().cursor()
        cursor.execute(query, (studentId,))
        theData = cursor.fetchall()
        
        # Debug print
        print(f"studentId={studentId}, raw query result={theData}")
        current_app.logger.info("studentId=%s, rows=%d", studentId, len(theData))

        # Convert to list of dicts for JSON
        theDataDict = [{"Club Name": row[0]} for row in theData]
        return jsonify(theDataDict)
    except Exception as e:
        current_app.logger.error("Error fetching clubs for studentId=%s: %s", studentId, str(e))
        return jsonify({"error": str(e)}), 500


# def club_mems(studentId):
#     query = """
#         SELECT clubName 
#         FROM club_members cm 
#         WHERE cm.studentId = %s
#     """
#     current_app.logger.info("GET /club_members/%s/clubs", studentId)
#     cursor = db.get_db().cursor()
#     cursor.execute(query, (studentId,))
#     theData = cursor.fetchall()
#     theDataDict = [{"Club Name": row[0]} for row in theData]
#     current_app.logger.info("GET /club_members/%s/clubs : rows=%d", studentId, len(theData))
#     response = make_response(jsonify(theDataDict))
#     response.status_code = 200
#     return response