from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for student-centric endpoints
students_api = Blueprint('students_api', __name__)

# ------------------------------------------------------------
# GET /api/students/<studentId>/gpa
# Purpose: Fetch a single student's GPA
@students_api.route('/students/<int:studentId>/gpa', methods=['GET'])
def student_gpa(studentId):
    query = "SELECT gpa FROM students WHERE userId = %s"
    current_app.logger.info("GET /students/%s/gpa", studentId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (studentId,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /students/%s/gpa : rows=%d", studentId, len(theData))
    response = make_response(jsonify(theData[0] if theData else {'gpa': None}))
    response.status_code = 200
    return response

# GET /api/students/gpas
# Purpose: Fetch all students' GPAs for histogram for Lim
@students_api.route('/students/gpas', methods=['GET'])
def all_students_gpas():
    query = "SELECT gpa, college FROM students WHERE gpa IS NOT NULL ORDER BY college"
    current_app.logger.info("GET /students/gpas")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /students/gpas : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/students/<studentId>/schedule
# Purpose: Class schedule for a student (courses, time, room)
@students_api.route('/students/<int:studentId>/schedule', methods=['GET'])
def student_schedule(studentId):
    query = '''
        SELECT c.name AS course_name,
               c.id   AS course_id,
               c.time,
               c.roomNumber,
               c.enrollment
        FROM students_courses sc
        JOIN courses c ON sc.courseId = c.id
        WHERE sc.studentId = %s
        ORDER BY c.time
    '''
    current_app.logger.info("GET /students/%s/schedule", studentId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (studentId,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /students/%s/schedule : rows=%d", studentId, len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/students/<studentId>/advisor
# Purpose: Get a student's advisor email address
@students_api.route('/students/<int:studentId>/advisor', methods=['GET'])
def student_advisor(studentId):
    query = '''
        SELECT u.emailAddress AS advisor_email
        FROM advisors a
        JOIN users u ON a.userId = u.userId
        JOIN students s ON a.userId = s.advisor
        WHERE s.userId = %s
    '''
    current_app.logger.info("GET /students/%s/advisor", studentId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (studentId,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /students/%s/advisor : rows=%d", studentId, len(theData))
    response = make_response(jsonify(theData[0] if theData else {'advisor_email': None}))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/students
# Purpose: List all students (with options to filter by college or year)
@students_api.route('/students', methods=['GET'])
def list_students():
    # Get query parameters
    college = request.args.get('college')
    year = request.args.get('year')
    # Base query
    query = "SELECT * FROM students JOIN users ON students.userId = users.userId"
    params = []
    # Add WHERE conditions if filters are provided
    conditions = []
    if college:
        conditions.append("students.college = %s")
        params.append(college)
    if year:
        conditions.append("students.year = %s") 
        params.append(year)
    # Add WHERE clause if we have any conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    current_app.logger.info("GET /students : listing students")
    cursor = db.get_db().cursor()
    cursor.execute(query, tuple(params))
    theData = cursor.fetchall()
    current_app.logger.info("GET /students : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# PATCH /api/students/<int:userId>
# Purpose: Update fields of a student
@students_api.route('/students/<int:userId>', methods=['PATCH'])
def update_student(userId): 
    payload = request.get_json(force=True, silent=True) or {}
    fields, params = [], []
    for k in ('year', 'housingStatus', 'race', 'income', 'origin', 'college', 'advisor'):
        if k in payload:
            fields.append(f"{k} = %s")
            params.append(payload[k])
    current_app.logger.info("PATCH /students/%s : fields=%s", userId, fields) 
    if not fields:
        response = make_response(jsonify({'updated': 0}))
        response.status_code = 200
        return response
    query = "UPDATE students SET " + ", ".join(fields) + " WHERE userId = %s"
    params.append(userId) 
    cursor = db.get_db().cursor()
    cursor.execute(query, tuple(params))
    db.get_db().commit()
    response = make_response(jsonify({'updated': 1}))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# DELETE /api/students/<int:userId>
# Purpose: Delete a student
@students_api.route('/students/<int:userId>', methods=['DELETE'])
def delete_student(userId):
    query = "DELETE FROM students WHERE userId = %s"
    current_app.logger.info("DELETE /students/%s", userId)
    cursor = db.get_db().cursor()
    cursor.execute(query, (userId,))
    db.get_db().commit()
    response = make_response(jsonify({}))
    response.status_code = 204
    return response