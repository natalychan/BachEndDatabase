from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for maintenance requests, staff hours, and tools linkage
maintenance_api = Blueprint('maintenance_api', __name__)

# ------------------------------------------------------------
# GET /api/maintenance-requests/staff/<int:userId>
# Purpose: List maintenance requests of a staff
@maintenance_api.route('/maintenance-requests/staff/<int:userId>', methods=['GET'])
def list_staff_requests(userId):
    # Main query with LEFT JOINs to get maintenance requests assigned to this staff member
    query = '''
        SELECT mr.orderId, mr.address, mr.problemType, mr.state, mr.submitted, mr.description,
               ms.staffId,
               u.firstName, u.lastName,
               GROUP_CONCAT(mrt.tool SEPARATOR ', ') as tools
        FROM maintenance_request AS mr
        LEFT JOIN maintenance_staffs_maintenance_request AS msmr ON mr.orderId = msmr.orderId
        LEFT JOIN maintenance_staffs AS ms ON msmr.staffId = ms.staffId
        LEFT JOIN users AS u ON mr.studentId = u.userId
        LEFT JOIN maintenance_request_tools AS mrt ON mr.orderId = mrt.orderId
        WHERE ms.staffId = %s
        GROUP BY mr.orderId, mr.address, mr.problemType, mr.state, mr.submitted, 
                 mr.description, ms.staffId, u.firstName, u.lastName
        ORDER BY mr.submitted DESC
    '''
    
    current_app.logger.info("GET /maintenance-requests/%s", userId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (userId,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /maintenance-requests/%s : rows=%d", userId, len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/maintenance-requests/student/<int:userId>
# Purpose: List maintenance requests submitted by a student
@maintenance_api.route('/maintenance-requests/student/<int:userId>', methods=['GET'])
def list_student_requests(userId):
    # Main query with LEFT JOINs to get maintenance requests assigned to this staff member
    query = '''
        SELECT mr.orderId, mr.address, mr.problemType, mr.state, mr.submitted, mr.description,
               ms.staffId,
               u.firstName, u.lastName,
               GROUP_CONCAT(mrt.tool SEPARATOR ', ') as tools
        FROM maintenance_request AS mr
        LEFT JOIN maintenance_staffs_maintenance_request AS msmr ON mr.orderId = msmr.orderId
        LEFT JOIN maintenance_staffs AS ms ON msmr.staffId = ms.staffId
        LEFT JOIN users AS u ON ms.staffId = u.userId
        LEFT JOIN maintenance_request_tools AS mrt ON mr.orderId = mrt.orderId
        WHERE mr.studentId = %s
        GROUP BY mr.orderId, mr.address, mr.problemType, mr.state, mr.submitted, 
                 mr.description, ms.staffId, u.firstName, u.lastName
        ORDER BY mr.submitted DESC
    '''
    
    current_app.logger.info("GET /maintenance-requests/%s", userId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (userId,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /maintenance-requests/%s : rows=%d", userId, len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# POST /api/maintenance-requests
# Purpose: Create a new maintenance request for a student
@maintenance_api.route('/maintenance-requests', methods=['POST'])
def create_maintenance_request():
    # Get the request data
    data = request.get_json()
    
    # Insert the maintenance request
    insert_query = '''
        INSERT INTO maintenance_request (address, problemType, description, studentId)
        VALUES (%s, %s, %s, %s)
    '''
    
    current_app.logger.info("POST /maintenance-requests")
    cursor = db.get_db().cursor()
    cursor.execute(insert_query, (
        data['address'],
        data['problemType'], 
        data['description'],
        data['studentId']
    ))
    
    # Get the newly created orderId
    new_order_id = cursor.lastrowid
    
    current_app.logger.info("POST /maintenance-requests : created orderId=%d", new_order_id)
    
    response_data = {
        "orderId": new_order_id,
        "message": "Maintenance request created successfully"
    }
    
    response = make_response(jsonify(response_data))
    response.status_code = 201
    return response

# ------------------------------------------------------------
# PATCH /api/maintenance-requests/update/<requestId>
# Purpose: Update fields on a maintenance request
@maintenance_api.route('/maintenance-requests/update/<int:requestId>', methods=['PATCH'])
def update_request(requestId):
    payload = request.get_json(force=True, silent=True) or {}
    fields, params = [], []
    for k in ('address','problemType','description','maintenanceStaffId','studentId','state'):
        if k in payload:
            fields.append(f"{k} = %s")
            params.append(payload[k])
    current_app.logger.info("PATCH /maintenance-requests/%s : fields=%s", requestId, fields)
    if not fields:
        response = make_response(jsonify({'updated': 0}))
        response.status_code = 200
        return response
    query = "UPDATE maintenance_request SET " + ", ".join(fields) + " WHERE orderId = %s"
    params.append(requestId)
    cursor = db.get_db().cursor()
    cursor.execute(query, tuple(params))
    db.get_db().commit()
    response = make_response(jsonify({'updated': 1}))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# DELETE /api/maintenance-requests/delete/<requestId>
# Purpose: Delete a maintenance request
@maintenance_api.route('/maintenance-requests/delete/<int:requestId>', methods=['DELETE'])
def delete_request(requestId):
    query = "DELETE FROM maintenance_request WHERE orderId = %s"
    current_app.logger.info("DELETE /maintenance-requests/%s", requestId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (requestId,))
    db.get_db().commit()
    response = make_response(jsonify({}))
    response.status_code = 204
    return response

# ------------------------------------------------------------
# GET /api/maintenance-staffs/<staffId>/hours
# Purpose: List logged work hours for a maintenance staffer
@maintenance_api.route('/maintenance-staffs/<int:staffId>/hours', methods=['GET'])
def get_hours(staffId):
    query = '''
        SELECT mr.orderId, msmr.workHours, mr.problemType, mr.state, mr.submitted
        FROM maintenance_request AS mr
        JOIN maintenance_staffs_maintenance_request AS msmr ON mr.orderId = msmr.orderId
        WHERE msmr.staffId = %s
        ORDER BY mr.submitted DESC
    '''
    current_app.logger.info("GET /maintenance-staffs/%s/hours", staffId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (staffId,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /maintenance-staffs/%s/hours : rows=%d", staffId, len(theData))
    response = make_response(jsonify({'staffId': staffId, 'entries': theData}))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/maintenance-requests/<requestId>/tools
# Purpose: List tools attached to a maintenance request
@maintenance_api.route('/maintenance-requests/<int:requestId>/get/tools', methods=['GET'])
def request_tools_list(requestId):
    query = '''
        SELECT mrt.tool, t.amount
        FROM maintenance_request_tools mrt
        JOIN tools t ON mrt.tool = t.productName
        WHERE mrt.orderId = %s
    '''
    current_app.logger.info("GET /maintenance-requests/%s/tools", requestId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (requestId,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /maintenance-requests/%s/tools : rows=%d", requestId, len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# POST /api/maintenance-requests/<requestId>/tools
# Purpose: Attach a tool to a maintenance request
@maintenance_api.route('/maintenance-requests/<int:requestId>/post/tools', methods=['POST'])
def request_tools_attach(requestId):
    payload = request.get_json(force=True, silent=True) or {}
    query = "INSERT INTO maintenance_request_tools (orderId, tool) VALUES (%s, %s)"
    current_app.logger.info("POST /maintenance-requests/%s/tools : payload=%s", requestId, payload)
    cursor = db.get_db().cursor()
    cursor.execute(query, (requestId, payload.get('tool')))
    db.get_db().commit()
    response = make_response(jsonify({'attached': True}))
    response.status_code = 201
    return response

# ------------------------------------------------------------
# DELETE /api/maintenance-requests/<requestId>/tools/<tool>
# Purpose: Detach a tool from a maintenance request
@maintenance_api.route('/maintenance-requests/<int:requestId>/delete/tools/<string:tool>', methods=['DELETE'])
def request_tools_detach(requestId, tool):
    query = "DELETE FROM maintenance_request_tools WHERE orderId = %s AND tool = %s"
    current_app.logger.info("DELETE /maintenance-requests/%s/tools/%s", requestId, tool)
    cursor = db.get_db().cursor()
    cursor.execute(query, (requestId, tool))
    db.get_db().commit()
    response = make_response(jsonify({}))
    response.status_code = 204
    return response
