from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for classroom availability and reservations
reserves_api = Blueprint('reservations_api', __name__)

# ------------------------------------------------------------
# GET /api/classrooms[?status=true|false]
# Purpose: List classrooms, optionally filter by availability status
@reserves_api.route('/classrooms', methods=['GET'])
def classrooms_list():
    status = request.args.get('status')
    params = []
    query = "SELECT roomNumber, status, lastMaintained FROM classrooms"
    if status is not None:
        query += " WHERE status = %s"
        params.append(status)
    current_app.logger.info("GET /classrooms : status=%s", status)
    cursor = db.get_db().cursor()
    cursor.execute(query, tuple(params))
    theData = cursor.fetchall()
    current_app.logger.info("GET /classrooms : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/classrooms/maintenance/recent?months=2
# Purpose: Show rooms maintained within the last N months (Maintenance / John-6)
@reserves_api.route('/classrooms/maintenance/recent', methods=['GET'])
def classrooms_recent_maintenance():
    months = int(request.args.get('months', 2))
    query = '''
        SELECT lastMaintained, roomNumber
        FROM classrooms
        WHERE lastMaintained >= DATE_SUB(NOW(), INTERVAL %s MONTH)
        ORDER BY lastMaintained
    '''
    current_app.logger.info("GET /classrooms/maintenance/recent : months=%s", months)
    cursor = db.get_db().cursor()
    cursor.execute(query, (months,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /classrooms/maintenance/recent : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# POST /api/reserves
# Purpose: Create a classroom reservation
@reserves_api.route('/reserves', methods=['POST'])
def create_reserve():
    payload = request.get_json(force=True, silent=True) or {}
    query = '''
        INSERT INTO reserves (studentID, roomNumber, startTime, endTime)
        VALUES (%s, %s, %s, %s)
    '''
    current_app.logger.info("POST /reserves : payload=%s", payload)
    cursor = db.get_db().cursor()
    cursor.execute(query, (payload.get('studentID'),
                           payload.get('roomNumber'),
                           payload.get('startTime'),
                           payload.get('endTime')))
    db.get_db().commit()
    response = make_response(jsonify({'created': True}))
    response.status_code = 201
    return response
