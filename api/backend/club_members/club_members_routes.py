from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db
# Blueprint for clubs listing
club_members_api = Blueprint('club_members_api', __name__)

# GET /api/students/<student_id>/clubs
# @club_members_api.route('/club_members/<int:studentId>/clubs', methods=['GET'])
@club_members_api.route('/club_members/<int:studentId>', methods=['GET'])
def club_members(studentId):
    query = 'SELECT * FROM club_members WHERE studentId = %s;'
    cursor = db.get_db().cursor()
    cursor.execute(query, (studentId,))
    theData = cursor.fetchall()
    return jsonify(theData)


