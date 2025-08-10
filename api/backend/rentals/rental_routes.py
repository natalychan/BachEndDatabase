from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for instrument rentals
rentals_api = Blueprint('rentals_api', __name__)

# ------------------------------------------------------------
# POST /api/rentals
# Purpose: Create a new instrument rental record
@rentals_api.route('/rentals', methods=['POST'])
def create_rental():
    payload = request.get_json(force=True, silent=True) or {}
    query = '''
        INSERT INTO rentals (studentID, instrumentID, startDate, returnDate)
        VALUES (%s, %s, %s, %s)
    '''
    current_app.logger.info("POST /rentals : payload=%s", payload)
    cursor = db.get_db().cursor()
    cursor.execute(query, (payload.get('studentId'),
                           payload.get('instrumentId'),
                           payload.get('startDate'),
                           payload.get('returnDate')))
    db.get_db().commit()
    response = make_response(jsonify({'created': True}))
    response.status_code = 201
    return response

# ------------------------------------------------------------
# PATCH /api/rentals/<rentalId>
# Purpose: Update an existing rental (e.g., set/extend return date)
@rentals_api.route('/rentals/<int:rentalId>', methods=['PATCH'])
def update_rental(rentalId):
    payload = request.get_json(force=True, silent=True) or {}
    query = "UPDATE rentals SET returnDate = %s WHERE rentalID = %s"
    current_app.logger.info("PATCH /rentals/%s : payload=%s", rentalId, payload)
    cursor = db.get_db().cursor()
    cursor.execute(query, (payload.get('returnDate'), rentalId))
    db.get_db().commit()
    response = make_response(jsonify({'updated': True}))
    response.status_code = 200
    return response
