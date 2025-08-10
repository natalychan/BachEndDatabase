from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for instruments inventory
instruments_api = Blueprint('instruments_api', __name__)

# ------------------------------------------------------------
# GET /api/instruments[?available=true|false]
# Purpose: List instruments, optionally filtering by availability
@instruments_api.route('/instruments', methods=['GET'])
def list_instruments():
    available = request.args.get('available')
    params = []
    query = "SELECT instrumentId, name, type, isAvailable FROM instruments"
    if available is not None:
        query += " WHERE isAvailable = %s"
        params.append(available.lower() in ('1', 'true', 't', 'yes'))
    current_app.logger.info("GET /instruments : available=%s", available)
    cursor = db.get_db().cursor()
    cursor.execute(query, tuple(params))
    theData = cursor.fetchall()
    current_app.logger.info("GET /instruments : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response
