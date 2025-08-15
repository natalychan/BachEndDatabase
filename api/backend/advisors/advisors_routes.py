from flask import Blueprint
from flask import request
from flask import jsonify
from flask import make_response
from flask import current_app
from backend.db_connection import db

#------------------------------------------------------------
# Create a new Blueprint object, which is a collection of 
# routes.
advisors_api = Blueprint('advisors_api', __name__)

#------------------------------------------------------------
# Get all the club from the database, package them up,
# and return them to the client
@advisors_api.route('/advisors/<int:student_id>', methods=['GET'])
def get_advisor_email(student_id):
    query = '''
        SELECT u.firstName, u.lastName, u.emailAddress
        FROM advisors a
        JOIN users u ON a.userId = u.userId
        JOIN students s ON a.userId = s.advisor
        where s.userId = %s
    '''
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(query, (student_id,))
    row = cursor.fetchone()

    if row:  
        result = {
            "advisor_name": f"{row['firstName']} {row['lastName']}",
            "emailAddress": row['emailAddress']
        }
        return jsonify(result), 200
    else:
        return jsonify({"error": "Student or advisor not found"}), 404