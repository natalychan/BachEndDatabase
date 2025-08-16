from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for maintenance requests, staff hours, and tools linkage
tools_api = Blueprint('tools_api', __name__)

# ------------------------------------------------------------
# GET /api/tools
# Purpose: List all tools and their amount
@tools_api.route('/tools', methods=['GET'])
def list_tools():
    query = "SELECT * FROM tools"
    current_app.logger.info("GET /tools : listing tools")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /tools : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# POST /api/tools
# Purpose: Create a new tool
@tools_api.route('/tools', methods=['POST'])
def create_tool():
    payload = request.get_json(force=True, silent=True) or {}
    query = '''
        INSERT INTO tools (amount, productName)
        VALUES (%s, %s)
    '''
    current_app.logger.info("POST /tools : payload=%s", payload)
    cursor = db.get_db().cursor()
    cursor.execute(query, (payload.get('amount'),
                           payload.get('productName')))
    db.get_db().commit()
    response = make_response(jsonify({'created': True}))
    response.status_code = 201
    return response

# ------------------------------------------------------------
# PATCH /api/tools/<productName>
# Purpose: Update fields of a tool
@tools_api.route('/tools/<string:productName>', methods=['PUT'])
def update_tool(productName): 
    payload = request.get_json(force=True, silent=True) or {}
    fields, params = [], []
    for k in ('amount','productName'):
        if k in payload:
            fields.append(f"{k} = %s")
            params.append(payload[k])
    current_app.logger.info("PUT /tools/%s : fields=%s", productName, fields) 
    if not fields:
        response = make_response(jsonify({'updated': 0}))
        response.status_code = 200
        return response
    query = "UPDATE tools SET " + ", ".join(fields) + " WHERE productName = %s"
    params.append(productName) 
    cursor = db.get_db().cursor()
    cursor.execute(query, tuple(params))
    db.get_db().commit()
    response = make_response(jsonify({'updated': 1}))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# DELETE /api/tools/<productName>
# Purpose: Delete a tool
@tools_api.route('/tools/<string:productName>', methods=['DELETE'])
def delete_tool(productName):
    query = "DELETE FROM tools WHERE productName = %s"
    current_app.logger.info("DELETE /tools/%s", productName)
    cursor = db.get_db().cursor()
    cursor.execute(query, (productName,))
    db.get_db().commit()
    response = make_response(jsonify({}))
    response.status_code = 204
    return response