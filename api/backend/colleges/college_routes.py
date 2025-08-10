from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for CRUD-ish college endpoints (create/delete)
colleges_api = Blueprint('colleges_api', __name__)

# ------------------------------------------------------------
# POST /api/colleges
# Purpose: Create (open) a college record
@colleges_api.route('/colleges', methods=['POST'])
def create_college():
    data = request.get_json(force=True, silent=True) or {}
    query = "INSERT INTO colleges (collegeName, dean, budget, status) VALUES (%s, %s, %s, %s)"
    current_app.logger.info("POST /colleges : payload=%s", data)
    cursor = db.get_db().cursor()
    cursor.execute(query, (data.get('collegeName'), data.get('dean'), data.get('budget'), data.get('status', True)))
    db.get_db().commit()
    response = make_response(jsonify({'collegeName': data.get('collegeName')}))
    response.status_code = 201
    return response

# ------------------------------------------------------------
# DELETE /api/colleges/<collegeName>
# Purpose: Delete (close) a college record
@colleges_api.route('/colleges/<string:collegeName>', methods=['DELETE'])
def delete_college(collegeName):
    query = "DELETE FROM colleges WHERE collegeName = %s"
    current_app.logger.info("DELETE /colleges/%s : deleting", collegeName)
    cursor = db.get_db().cursor()
    cursor.execute(query, (collegeName,))
    db.get_db().commit()
    response = make_response(jsonify({}))
    response.status_code = 204
    return response
