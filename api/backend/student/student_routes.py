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
    query = "SELECT gpa FROM students WHERE gpa IS NOT NULL ORDER BY college"
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
