# president will get demographic information about all students
@metrics.route('/metrics', methods=['GET'])
def get_student_demographics ():
    query = f'''select 'origin' as type,
                origin as category,
                count(*) as num_students,
                round (100* count(*)/sum(count(*)) over(), 2) as percentage
                from students
                group by origin

                union all

                select 'housingStatus'as type,
                housingStatus as category,
                count(*) as num_students,
                round (100*count(*)) over (),2) as percentage
                from students
                group by housingStatus

                union all

                select 'race' as type,
                race as category, 
                count(*) as num_students,
                round (100*count(*)) over (),2) as percentage
                from students 
                group by race;
    '''
    
    # logging the query for debugging purposes.  
    # The output will appear in the Docker logs output
    # This line has nothing to do with actually executing the query...
    # It is only for debugging purposes. 
    current_app.logger.info(f'GET /metrics query={query}')

    # get the database connection, execute the query, and 
    # fetch the results as a Python Dictionary
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    
    # Another example of logging for debugging purposes.
    # You can see if the data you're getting back is what you expect. 
    current_app.logger.info(f'GET /metrics Result of query = {theData}')
    
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response
    