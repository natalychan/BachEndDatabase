# GET /api/students/<student_id>/clubs
@clubs_api.route('/club_members', methods=['GET'])
def club_mems(student_id):
    query = """
        SELECT cm.clubName AS club_name
        FROM club_members cm
        WHERE cm.studentId = %s
    """
    cursor = db.get_db().cursor()
    cursor.execute(query, (student_id,))
    theData = cursor.fetchall()
    
    # Convert tuples to dicts
    theDataDict = [{'club_name': row[0], 'role': row[1]} for row in theData]
    
    response = make_response(jsonify(theDataDict))
    response.status_code = 200
    return response
