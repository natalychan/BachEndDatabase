from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import db

# Blueprint for metrics and college-wide reporting
metrics_api = Blueprint('metrics_api', __name__)

# ------------------------------------------------------------
# GET /api/colleges/averages/gpa
# Purpose: Average student GPA by college (President / Lim-1)
@metrics_api.route('/colleges/averages/gpa', methods=['GET'])
def colleges_avg_gpa():
    query = '''
        SELECT college, ROUND(AVG(gpa), 2) AS average_gpa
        FROM students
        GROUP BY college
        ORDER BY average_gpa DESC
    '''
    current_app.logger.info("GET /colleges/averages/gpa : computing avg GPA by college")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /colleges/averages/gpa : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/metrics/demographics
# Purpose: Overall demographics (origin, housingStatus, race) with percentages of entire student body
@metrics_api.route('/metrics/demographics', methods=['GET'])
def demographics_overall():
    query = '''
        SELECT 'origin' AS type,
               origin   AS category,
               COUNT(*) AS num_students,
               ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM students
        GROUP BY origin

        UNION ALL

        SELECT 'housingStatus' AS type,
               housingStatus   AS category,
               COUNT(*)        AS num_students,
               ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM students
        GROUP BY housingStatus

        UNION ALL

        SELECT 'race' AS type,
               race   AS category,
               COUNT(*) AS num_students,
               ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM students
        GROUP BY race

        UNION ALL

        SELECT 'incomeBracket' AS type,
               CASE 
                   WHEN income < 25000 THEN '<$25k'
                   WHEN income BETWEEN 25000 AND 49999 THEN '$25k–$50k'
                   WHEN income BETWEEN 50000 AND 74999 THEN '$50k–$75k'
                   ELSE '$75k+'
               END AS category,
               COUNT(*) AS num_students,
               ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM students
        GROUP BY category
    '''
    current_app.logger.info("GET /metrics/demographics : overall demographics with percentages")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /metrics/demographics : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/<CollegeName>/enrollment-trend
# Purpose: Year-by-year enrollment counts for a college
@metrics_api.route('/colleges/<string:collegeName>/enrollment-trend', methods=['GET'])
def college_enrollment_trend(collegeName):
    # by=year for now; easy to extend to term/semester later
    query = '''
        SELECT s.year AS period, COUNT(*) AS enrollment
        FROM students s
        WHERE s.college = %s
        GROUP BY s.year
        ORDER BY s.year
    '''
    current_app.logger.info("GET /colleges/%s/enrollment-trend", collegeName)
    cursor = db.get_db().cursor()
    cursor.execute(query, (collegeName,))
    rows = cursor.fetchall()  # e.g., [{'period': 1, 'enrollment': 240}, ...]
    response = make_response(jsonify(rows))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/<collegeName>/demographics
# Purpose: Demographics (origin, housingStatus, race) within a single college with within-college percentages
@metrics_api.route('/colleges/<string:collegeName>/demographics', methods=['GET'])
def demographics_by_college(collegeName):
    query = '''
        SELECT 'origin' AS type,
               origin   AS category,
               COUNT(*) AS num_students,
               ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM students
        WHERE college = %s
        GROUP BY origin

        UNION ALL

        SELECT 'housingStatus' AS type,
               housingStatus   AS category,
               COUNT(*)        AS num_students,
               ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM students
        WHERE college = %s
        GROUP BY housingStatus

        UNION ALL

        SELECT 'race' AS type,
               race   AS category,
               COUNT(*) AS num_students,
               ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM students
        WHERE college = %s
        GROUP BY race
    '''
    current_app.logger.info("GET /colleges/%s/demographics : per-college demographics", collegeName)
    cursor = db.get_db().cursor()
    cursor.execute(query, (collegeName, collegeName, collegeName))
    theData = cursor.fetchall()
    current_app.logger.info("GET /colleges/%s/demographics : rows=%d", collegeName, len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/courses/vacancies
# Purpose: List courses with a vacancy flag (no professor assigned) (President / Lim-3)
@metrics_api.route('/courses/vacancies', methods=['GET'])
def courses_vacancies():
    query = '''
        SELECT c.id      AS course_id,
               c.name    AS course_name,
               c.time,
               c.enrollment,
               (c.id NOT IN (SELECT courseId FROM professors_courses)) AS is_vacant
        FROM courses c
        ORDER BY is_vacant DESC, c.name
    '''
    current_app.logger.info("GET /courses/vacancies : listing course vacancies")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /courses/vacancies : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/metrics/student-teacher-ratio
# Purpose: Student-to-teacher ratio by college (President / Lim-5)
@metrics_api.route('/colleges/metrics/student-teacher-ratio', methods=['GET'])
def student_teacher_ratio():
    query = '''
        SELECT s.college,
               COUNT(DISTINCT s.userId) AS num_students,
               COUNT(DISTINCT pc.professorId) AS num_professors,
               ROUND(COUNT(DISTINCT s.userId) * 1.0 / NULLIF(COUNT(DISTINCT pc.professorId), 0), 2) AS student_teacher_ratio
        FROM students s
        LEFT JOIN students_courses sc ON sc.studentId = s.userId
        LEFT JOIN professors_courses pc ON pc.courseId = sc.courseId
        GROUP BY s.college
        ORDER BY student_teacher_ratio DESC
    '''
    current_app.logger.info("GET /colleges/metrics/student-teacher-ratio : computing ratios")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /colleges/metrics/student-teacher-ratio : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/rankings/compare
# Purpose: retrieves national rankings (President / Lim-6)
@metrics_api.route('/rankings/compare', methods=['GET'])
def rankings_compare():
    query = '''
        SELECT *
        FROM school_rankings sr
        ORDER BY sr.ranking ASC
    '''
    current_app.logger.info("GET /rankings/compare : comparing GPA vs rankings")
    cursor = db.get_db().cursor()
    cursor.execute(query)
    theData = cursor.fetchall()
    current_app.logger.info("GET /rankings/compare : rows=%d", len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/<collegeName>/enrollment
# Purpose: Total enrollment for a college (Dean / Yo-1)
@metrics_api.route('/colleges/<string:collegeName>/enrollment', methods=['GET'])
def college_enrollment(collegeName):
    query = '''
        SELECT COUNT(*) AS total_enrollment
        FROM students
        WHERE college = %s
    '''
    current_app.logger.info("GET /colleges/%s/enrollment : fetching count", collegeName)
    cursor = db.get_db().cursor()
    cursor.execute(query, (collegeName,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /colleges/%s/enrollment : rows=%d", collegeName, len(theData))
    response = make_response(jsonify(theData[0] if theData else {'total_enrollment': 0}))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/<collegeName>/course-enrollments
# Purpose: Enrollment counts per course in a college (Dean / Yo-2)
@metrics_api.route('/colleges/<string:collegeName>/course-enrollments', methods=['GET'])
def college_course_enrollments(collegeName):
    query = '''
        SELECT c.name AS course_name,
               c.id   AS course_id,
               COUNT(sc.studentId) AS enrolled_students
        FROM courses c
        LEFT JOIN students_courses sc ON sc.courseId = c.id
        WHERE c.college = %s
        GROUP BY c.id, c.name
        ORDER BY enrolled_students DESC
    '''
    current_app.logger.info("GET /colleges/%s/course-enrollments : listing", collegeName)
    cursor = db.get_db().cursor()
    cursor.execute(query, (collegeName,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /colleges/%s/course-enrollments : rows=%d", collegeName, len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/<collegeName>/budget
# Purpose: Get budget/status/dean for a college (Dean / Yo-3)
@metrics_api.route('/colleges/<string:collegeName>/budget', methods=['GET'])
def college_budget(collegeName):
    query = '''
        SELECT collegeName, budget, status, dean
        FROM colleges
        WHERE collegeName = %s
    '''
    current_app.logger.info("GET /colleges/%s/budget : fetching", collegeName)
    cursor = db.get_db().cursor()
    cursor.execute(query, (collegeName,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /colleges/%s/budget : rows=%d", collegeName, len(theData))
    response = make_response(jsonify(theData[0] if theData else {}))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/<collegeName>/performance
# Purpose: Performance summary for a college (avg GPA + by course + by professor) (Dean / Yo-4)
@metrics_api.route('/colleges/<string:collegeName>/performance', methods=['GET'])
def college_performance(collegeName):
    cursor = db.get_db().cursor()
    current_app.logger.info("GET /colleges/%s/performance : starting", collegeName)

    avg_gpa_q = "SELECT ROUND(AVG(gpa), 2) AS avg_gpa FROM students WHERE college = %s"
    cursor.execute(avg_gpa_q, (collegeName,))
    avg_gpa = cursor.fetchall()
    avg_val = avg_gpa[0].get('avg_gpa') if avg_gpa else None
    current_app.logger.debug("GET /colleges/%s/performance : avg_gpa=%s", collegeName, avg_val)

    by_course_q = '''
        SELECT c.id AS course_id,
               c.name AS course_name,
               ROUND(AVG(s.gpa), 2) AS avg_student_gpa
        FROM courses c
        LEFT JOIN students_courses sc ON sc.courseId = c.id
        LEFT JOIN students s ON sc.studentId = s.userId
        WHERE c.college = %s
        GROUP BY c.id, c.name
        ORDER BY avg_student_gpa DESC
    '''
    cursor.execute(by_course_q, (collegeName,))
    by_course = cursor.fetchall()
    current_app.logger.debug("GET /colleges/%s/performance : by_course rows=%d", collegeName, len(by_course))

    by_prof_q = '''
        SELECT p.userId AS professor,
               u.firstName,
               u.lastName,
               ROUND(AVG(s.gpa), 2) AS avg_student_gpa
        FROM professors p
        JOIN professors_courses pc ON pc.professorId = p.userId
        JOIN courses c ON c.id = pc.courseId
        JOIN students_courses sc ON sc.courseId = c.id
        JOIN students s ON sc.studentId = s.userId
        JOIN users u ON p.userId = u.userId
        WHERE c.college = %s
        GROUP BY p.userId, u.firstName, u.lastName
        ORDER BY avg_student_gpa DESC
    '''
    cursor.execute(by_prof_q, (collegeName,))
    by_prof = cursor.fetchall()
    current_app.logger.debug("GET /colleges/%s/performance : by_prof rows=%d", collegeName, len(by_prof))

    response = make_response(jsonify({
        "college": collegeName,
        "avg_gpa": avg_val,
        "by_course": by_course,
        "by_professor": by_prof
    }))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/<collegeName>/students?gpaMin=
# Purpose: List high-performing students in a college (Dean / Yo-5)
@metrics_api.route('/colleges/<string:collegeName>/students', methods=['GET'])
def high_performers(collegeName):
    gpa_min = request.args.get('gpaMin', default=3.5, type=float)
    query = '''
        SELECT s.userId,
               u.firstName,
               u.lastName,
               s.gpa,
               sr.ranking AS school_rank
        FROM students s
        JOIN users u ON s.userId = u.userId
        JOIN school_rankings sr ON s.college = sr.schoolName
        WHERE s.college = %s AND s.gpa >= %s
        ORDER BY s.gpa DESC, sr.ranking ASC
    '''
    current_app.logger.info("GET /colleges/%s/students : gpaMin=%s", collegeName, gpa_min)
    cursor = db.get_db().cursor()
    cursor.execute(query, (collegeName, gpa_min))
    theData = cursor.fetchall()
    current_app.logger.info("GET /colleges/%s/students : rows=%d", collegeName, len(theData))
    response = make_response(jsonify(theData))
    response.status_code = 200
    return response

# ------------------------------------------------------------
# GET /api/colleges/<collegeName>/alumni/placements
# Purpose: Alumni employment counts & rate (Dean / Yo-6)
@metrics_api.route('/colleges/<string:collegeName>/alumni/placements', methods=['GET'])
def alumni_placements(collegeName):
    query = '''
        SELECT s.college,
               COUNT(*) AS total_alumni,
               SUM(a.hasJob = 'true') AS employed_alumni,
               ROUND(SUM(a.hasJob = 'true') * 1.0 / COUNT(*), 2) AS employment_rate
        FROM alumni a
        JOIN students s ON a.studentId = s.userId
        WHERE s.college = %s
        GROUP BY s.college
        ORDER BY employment_rate DESC
    '''
    current_app.logger.info("GET /colleges/%s/alumni/placements : fetching", collegeName)
    cursor = db.get_db().cursor()
    cursor.execute(query, (collegeName,))
    theData = cursor.fetchall()
    current_app.logger.info("GET /colleges/%s/alumni/placements : rows=%d", collegeName, len(theData))
    response = make_response(jsonify(theData[0] if theData else {'college': collegeName, 'total_alumni': 0, 'employed_alumni': 0, 'employment_rate': None}))
    response.status_code = 200
    return response

# ------ Dean-specific helpers & routes ------

def _as_num(v, default=0):
    try:
        return float(v) if v is not None else default
    except Exception:
        return default

def _college_for_dean_id(dean_id: int):
    q = "SELECT c.collegeName FROM colleges c WHERE c.dean = %s LIMIT 1"
    cur = db.get_db().cursor()
    cur.execute(q, (dean_id,))
    return cur.fetchone()

@metrics_api.route("/metrics/deans/<int:dean_id>/college", methods=["GET"])
def dean_college(dean_id: int):
    row = _college_for_dean_id(dean_id)
    return make_response(jsonify(row or {}), 200)

@metrics_api.route("/metrics/deans/<int:dean_id>/courses", methods=["GET"])
def dean_courses(dean_id: int):
    col = _college_for_dean_id(dean_id)
    if not col or not col.get("collegeName"):
        return make_response(jsonify([]), 200)

    q = """
        SELECT c.id AS course_id, c.name AS course_name,
               COALESCE(c.enrollment, 0) AS enrollment,
               0 AS capacity,
               NULL AS vacancies
        FROM courses c
        WHERE c.college = %s
        ORDER BY c.name
    """
    cur = db.get_db().cursor()
    cur.execute(q, (col["collegeName"],))
    rows = cur.fetchall() or []
    for r in rows:
        r["enrollment"] = int(_as_num(r.get("enrollment"), 0))
        r["capacity"] = int(_as_num(r.get("capacity"), 0))
    return make_response(jsonify(rows), 200)

@metrics_api.route("/metrics/courses/averages/gpa", methods=["GET"])
def course_averages_gpa():
    """
    Returns: [{course_id, course_name, average_gpa}]
    Optional filter: ?college=Name
    """
    college = request.args.get("college")
    cur = db.get_db().cursor()
    if college:
        q = """
            SELECT c.id AS course_id, c.name AS course_name, ROUND(AVG(s.gpa), 2) AS average_gpa
            FROM students_courses sc
            JOIN students s ON s.userId = sc.studentId
            JOIN courses  c ON c.id = sc.courseId
            WHERE c.college = %s
            GROUP BY c.id, c.name
            ORDER BY c.name
        """
        cur.execute(q, (college,))
    else:
        q = """
            SELECT c.id AS course_id, c.name AS course_name, ROUND(AVG(s.gpa), 2) AS average_gpa
            FROM students_courses sc
            JOIN students s ON s.userId = sc.studentId
            JOIN courses  c ON c.id = sc.courseId
            GROUP BY c.id, c.name
            ORDER BY c.name
        """
        cur.execute(q)
    return make_response(jsonify(cur.fetchall()), 200)


@metrics_api.route('/courses/vacancies', methods=['GET'])
def courses_vacancies_filtered():
    college = request.args.get("college")
    cur = db.get_db().cursor()
    if college:
        q = """
            SELECT c.id AS course_id, c.name AS course_name, c.time, c.enrollment,
                   ((c.professorId IS NULL) OR
                    (c.id NOT IN (SELECT pc.courseId FROM professors_courses pc))) AS is_vacant
            FROM courses c
            WHERE c.college = %s
            ORDER BY is_vacant DESC, c.name
        """
        cur.execute(q, (college,))
    else:
        q = """
            SELECT c.id AS course_id, c.name AS course_name, c.time, c.enrollment,
                   ((c.professorId IS NULL) OR
                    (c.id NOT IN (SELECT pc.courseId FROM professors_courses pc))) AS is_vacant
            FROM courses c
            ORDER BY is_vacant DESC, c.name
        """
        cur.execute(q)
    return make_response(jsonify(cur.fetchall()), 200)

@metrics_api.route("/metrics/courses/<int:course_id>/enrollment-trend", methods=["GET"])
def course_enrollment_trend(course_id: int):
    q = """
        SELECT s.year AS period, COUNT(*) AS enrollment
        FROM students_courses sc
        JOIN students s ON s.userId = sc.studentId
        WHERE sc.courseId = %s
        GROUP BY s.year
        ORDER BY s.year
    """
    cur = db.get_db().cursor()
    cur.execute(q, (course_id,))
    return make_response(jsonify(cur.fetchall()), 200)

@metrics_api.route("/metrics/courses/student-teacher-ratio", methods=["GET"])
def course_student_teacher_ratio():
    """
    Returns: [{course_name, students_per_teacher}]
    Optional filter: ?college=Name
    """
    college = request.args.get("college")
    cur = db.get_db().cursor()

    # Base course list (filter by college if provided)
    if college:
        cur.execute("""
            SELECT id AS course_id, name AS course_name, enrollment
            FROM courses
            WHERE college = %s
        """, (college,))
    else:
        cur.execute("""
            SELECT id AS course_id, name AS course_name, enrollment
            FROM courses
        """)
    courses = cur.fetchall()

    def _as_num(v, d=0):
        try:
            return float(v) if v is not None else d
        except Exception:
            return d

    results = []
    for c in courses:
        cid = c["course_id"]

        # Enrollment: prefer courses.enrollment; fallback to students_courses count
        enrolled = _as_num(c.get("enrollment"), 0)
        if not enrolled:
            cur.execute("SELECT COUNT(*) AS cnt FROM students_courses WHERE courseId = %s", (cid,))
            enrolled = _as_num(cur.fetchone()["cnt"], 0)

        # Instructors from professors_courses
        cur.execute("SELECT COUNT(*) AS icnt FROM professors_courses WHERE courseId = %s", (cid,))
        icnt = _as_num(cur.fetchone()["icnt"], 0)

        ratio = (enrolled / icnt) if icnt else None
        results.append({
            "course_name": c["course_name"],
            "students_per_teacher": ratio
        })

    return make_response(jsonify(results), 200)


@metrics_api.route("/metrics/courses/budget", methods=["GET"])
def course_budget_direct():
    """
    Returns the stored budget per course, optionally filtered by college.o
    Requires `courses.budget` to exist (DECIMAL/NUMERIC).
    [{course_id, course_name, budget}]
    """
    college = request.args.get("college")
    cur = db.get_db().cursor()
    if college:
        cur.execute("""
            SELECT id AS course_id, name AS course_name, COALESCE(budget, 0) AS budget
            FROM courses
            WHERE college = %s
            ORDER BY name
        """, (college,))
    else:
        cur.execute("""
            SELECT id AS course_id, name AS course_name, COALESCE(budget, 0) AS budget
            FROM courses
            ORDER BY name
        """)
    return make_response(jsonify(cur.fetchall()), 200)

@metrics_api.route("/metrics/courses/<int:course_id>/students", methods=["GET"])
def course_students(course_id: int):
    """
    ?gpaMin=3.5 (default)
    Returns: [{userId, firstName, lastName, gpa, school_rank}]
    """
    gpa_min = request.args.get('gpaMin', default=3.5, type=float)
    cur = db.get_db().cursor()
    q = """
        SELECT s.userId,
               u.firstName,
               u.lastName,
               s.gpa,
               sr.ranking AS school_rank
        FROM students_courses sc
        JOIN students s ON s.userId = sc.studentId
        JOIN users   u  ON u.userId = s.userId
        LEFT JOIN school_rankings sr ON s.college = sr.schoolName
        WHERE sc.courseId = %s AND s.gpa >= %s
        ORDER BY s.gpa DESC, u.lastName, u.firstName
        LIMIT 100
    """
    cur.execute(q, (course_id, gpa_min))
    return make_response(jsonify(cur.fetchall()), 200)

@metrics_api.route("/metrics/courses/enrollments", methods=["GET"])
def courses_enrollments_list():
    """
    Returns: [{course_id, course_name, enrolled_students}]
    Optional: ?college=Name
    """
    college = request.args.get("college")
    cur = db.get_db().cursor()
    if college:
        cur.execute("""
            SELECT id AS course_id, name AS course_name, COALESCE(enrollment, 0) AS enrolled_students
            FROM courses
            WHERE college = %s
            ORDER BY enrolled_students DESC, name
        """, (college,))
    else:
        cur.execute("""
            SELECT id AS course_id, name AS course_name, COALESCE(enrollment, 0) AS enrolled_students
            FROM courses
            ORDER BY enrolled_students DESC, name
        """)
    return make_response(jsonify(cur.fetchall()), 200)

# =========================
# Dean Budget / Finance APIs (matches final schema)
# =========================

@metrics_api.route("/metrics/deans/<int:dean_id>/budget/summary", methods=["GET"])
def dean_budget_summary(dean_id: int):
    """
    Returns: totalBudget, totalDonations, budgetUsed, remaining
    for the dean's college.
    """
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify({})

    q = """
        SELECT
            COALESCE(SUM(c.budget), 0) AS totalBudget,
            COALESCE(SUM(d.amount), 0) AS totalDonations,
            COALESCE(SUM(e.amount), 0) AS budgetUsed,
            (COALESCE(SUM(c.budget),0) + COALESCE(SUM(d.amount),0)
             - COALESCE(SUM(e.amount),0)) AS remaining
        FROM courses c
        LEFT JOIN course_donations d ON d.courseId = c.id
        LEFT JOIN course_expenses e  ON e.courseId = c.id
        WHERE c.college = %s
    """
    cur = db.get_db().cursor()
    cur.execute(q, (college,))
    return jsonify(cur.fetchone() or {})


@metrics_api.route("/metrics/deans/<int:dean_id>/budget/spending-trend", methods=["GET"])
def dean_spending_trend(dean_id: int):
    """
    Time-series of spending (sum of course_expenses.amount) for the dean's college.
    Returns rows like: [{ "period": <date>, "spending": <number> }]
    Optional: ?by=month to aggregate by month instead of by day.
    """
    # Get the dean's college
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify([])

    # Allow aggregation choice: daily (default) or monthly
    by = (request.args.get("by") or "day").lower()
    if by == "month":
        # Aggregate by first day of each month
        q = """
            SELECT
                DATE_FORMAT(e.spentAt, '%%Y-%%m-01') AS period,
                COALESCE(SUM(e.amount), 0) AS spending
            FROM course_expenses e
            JOIN courses c ON c.id = e.courseId
            WHERE c.college = %s
            GROUP BY DATE_FORMAT(e.spentAt, '%%Y-%%m-01')
            ORDER BY DATE_FORMAT(e.spentAt, '%%Y-%%m-01')
        """
        params = (college,)
    else:
        # Default: daily aggregation
        q = """
            SELECT
                e.spentAt AS period,
                COALESCE(SUM(e.amount), 0) AS spending
            FROM course_expenses e
            JOIN courses c ON c.id = e.courseId
            WHERE c.college = %s
            GROUP BY e.spentAt
            ORDER BY e.spentAt
        """
        params = (college,)

    # Run the query
    cur = db.get_db().cursor()
    cur.execute(q, params)
    rows = cur.fetchall()

    # Return the results
    return jsonify(rows)




@metrics_api.route("/metrics/deans/<int:dean_id>/budget/by-course", methods=["GET"])
def dean_budget_by_course(dean_id: int):
    """
    Department/Course financial breakdown.
    """
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify([])

    q = """
        SELECT
            c.id AS courseId,
            c.name AS courseName,
            COALESCE(c.budget, 0) AS allocated,
            COALESCE(SUM(DISTINCT d.amount), 0) AS donations,
            COALESCE(SUM(DISTINCT e.amount), 0) AS used,
            (COALESCE(c.budget,0) + COALESCE(SUM(DISTINCT d.amount),0)) AS total,
            CASE 
              WHEN (COALESCE(c.budget,0) + COALESCE(SUM(DISTINCT d.amount),0)) > 0
              THEN ROUND(100 * COALESCE(SUM(DISTINCT e.amount),0) 
                         / (COALESCE(c.budget,0) + COALESCE(SUM(DISTINCT d.amount),0)), 2)
              ELSE NULL
            END AS usedPct
        FROM courses c
        LEFT JOIN course_donations d ON d.courseId = c.id
        LEFT JOIN course_expenses e  ON e.courseId = c.id
        WHERE c.college = %s
        GROUP BY c.id, c.name, c.budget
        ORDER BY c.name
    """
    cur = db.get_db().cursor()
    cur.execute(q, (college,))
    return jsonify(cur.fetchall())


@metrics_api.route("/metrics/deans/<int:dean_id>/budget/donations", methods=["GET"])
def dean_budget_donations(dean_id: int):
    """
    Latest donations table for this dean's college.
    """
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify([])

    limit = max(1, min(int(request.args.get("limit", 25)), 500))
    q = f"""
        SELECT
            d.donorName AS donor,
            d.amount AS amount,
            d.donatedAt AS date,
            c.name AS courseName
        FROM course_donations d
        JOIN courses c ON c.id = d.courseId
        WHERE c.college = %s
        ORDER BY d.donatedAt DESC, d.donationId DESC
        LIMIT {limit}
    """
    cur = db.get_db().cursor()
    cur.execute(q, (college,))
    return jsonify(cur.fetchall())


@metrics_api.route("/metrics/deans/<int:dean_id>/budget/donations-by-course", methods=["GET"])
def dean_donations_by_course(dean_id: int):
    """
    Bar chart: total donations grouped by course for this dean's college.
    """
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify([])

    q = """
        SELECT
            c.name AS courseName,
            COALESCE(SUM(d.amount), 0) AS donations
        FROM courses c
        LEFT JOIN course_donations d ON d.courseId = c.id
        WHERE c.college = %s
        GROUP BY c.name
        ORDER BY donations DESC, c.name
    """
    cur = db.get_db().cursor()
    cur.execute(q, (college,))
    return jsonify(cur.fetchall())

# ---------------- Alumni placement (Dean) ------------------

@metrics_api.route("/metrics/deans/<int:dean_id>/alumni/placement/summary", methods=["GET"])
def dean_alumni_placement_summary(dean_id: int):
    """Overall alumni placement summary for the dean's college."""
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify({})

    q = '''
        SELECT
            COUNT(*) AS totalAlumni,
            SUM(CASE WHEN a.hasJob THEN 1 ELSE 0 END) AS placed,
            ROUND(100 * SUM(CASE WHEN a.hasJob THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS placementRate
        FROM alumni a
        JOIN students s ON s.userId = a.studentId
        WHERE s.college = %s
    '''
    cur = db.get_db().cursor()
    cur.execute(q, (college,))
    row = cur.fetchone() or {"totalAlumni": 0, "placed": 0, "placementRate": 0.0}
    return jsonify(row)


@metrics_api.route("/metrics/deans/<int:dean_id>/alumni/placement/by-course", methods=["GET"])
def dean_alumni_placement_by_course(dean_id: int):
    """Placement rate by course within the dean's college."""
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify([])

    q = '''
        SELECT
            c.id AS courseId,
            c.name AS courseName,
            COUNT(*) AS alumniCount,
            SUM(CASE WHEN a.hasJob THEN 1 ELSE 0 END) AS placed,
            ROUND(100 * SUM(CASE WHEN a.hasJob THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS placementRate,
            ROUND(AVG(s.gpa), 2) AS avgGpa
        FROM alumni a
        JOIN students s         ON s.userId = a.studentId
        JOIN students_courses sc ON sc.studentId = a.studentId
        JOIN courses c          ON c.id = sc.courseId
        WHERE c.college = %s
        GROUP BY c.id, c.name
        ORDER BY placementRate DESC, alumniCount DESC, c.name
    '''
    cur = db.get_db().cursor()
    cur.execute(q, (college,))
    return jsonify(cur.fetchall())


@metrics_api.route("/metrics/deans/<int:dean_id>/alumni/placement/by-year", methods=["GET"])
def dean_alumni_placement_by_year(dean_id: int):
    """Placement trend by student year (proxy for cohort) in the dean's college."""
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify([])

    q = '''
        SELECT
            s.year AS year,
            COUNT(*) AS alumniCount,
            SUM(CASE WHEN a.hasJob THEN 1 ELSE 0 END) AS placed,
            ROUND(100 * SUM(CASE WHEN a.hasJob THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS placementRate
        FROM alumni a
        JOIN students s ON s.userId = a.studentId
        WHERE s.college = %s
        GROUP BY s.year
        ORDER BY s.year
    '''
    cur = db.get_db().cursor()
    cur.execute(q, (college,))
    return jsonify(cur.fetchall())

@metrics_api.route("/metrics/deans/<int:dean_id>/students/enrollment-total", methods=["GET"])
def dean_total_students_enrollment(dean_id: int):
    """
    Total number of students enrolled in the dean's college.
    Returns: { "totalEnrollment": <int> }
    """
    row = _college_for_dean_id(dean_id)
    college = (row or {}).get("collegeName")
    if not college:
        return jsonify({"totalEnrollment": 0})

    q = """
        SELECT COUNT(*) AS totalEnrollment
        FROM students s
        WHERE s.college = %s
    """
    cur = db.get_db().cursor()
    cur.execute(q, (college,))
    result = cur.fetchone() or {"totalEnrollment": 0}
    try:
        result["totalEnrollment"] = int(result.get("totalEnrollment") or 0)
    except Exception:
        result["totalEnrollment"] = 0
    return jsonify(result)


# =========================
# President Budget / Finance APIs 
# =========================
@metrics_api.route("/metrics/president/budget/summary", methods=["GET"])
def president_budget_summary():
    """
    Overall budget summary for each college: budget, donations, spending, remaining.
    """
    q = """
        SELECT
            c.college AS collegeName,
            COALESCE(SUM(c.budget), 0) AS totalBudget,
            COALESCE(SUM(d.amount), 0) AS totalDonations,
            COALESCE(SUM(e.amount), 0) AS budgetUsed,
            (COALESCE(SUM(c.budget),0) + COALESCE(SUM(d.amount),0)
             - COALESCE(SUM(e.amount),0)) AS remaining
        FROM courses c
        LEFT JOIN course_donations d ON d.courseId = c.id
        LEFT JOIN course_expenses e  ON e.courseId = c.id
        GROUP BY c.college
        ORDER BY c.college
    """
    cur = db.get_db().cursor()
    cur.execute(q)
    return jsonify(cur.fetchall())

@metrics_api.route("/metrics/president/budget/spending-trend", methods=["GET"])
def president_spending_trend():
    """
    Time-series of spending for all colleges.
    Pass ?by=month to aggregate by month.
    """
    by = (request.args.get("by") or "day").lower()
    if by == "month":
        q = """
            SELECT
                c.college AS collegeName,
                DATE_FORMAT(e.spentAt, '%%Y-%%m-01') AS period,
                COALESCE(SUM(e.amount), 0) AS spending
            FROM course_expenses e
            JOIN courses c ON c.id = e.courseId
            GROUP BY c.college, DATE_FORMAT(e.spentAt, '%%Y-%%m-01')
            ORDER BY c.college, period
        """
    else:
        q = """
            SELECT
                c.college AS collegeName,
                e.spentAt AS period,
                COALESCE(SUM(e.amount), 0) AS spending
            FROM course_expenses e
            JOIN courses c ON c.id = e.courseId
            GROUP BY c.college, e.spentAt
            ORDER BY c.college, period
        """

    cur = db.get_db().cursor()
    cur.execute(q)
    return jsonify(cur.fetchall())

@metrics_api.route("/metrics/president/budget/by-course", methods=["GET"])
def president_budget_by_course():
    """
    Budget usage broken down by course for each college.
    """
    q = """
        SELECT
            c.college AS collegeName,
            c.name,
            COALESCE(c.budget, 0) AS budget,
            COALESCE(SUM(e.amount), 0) AS budgetUsed,
            (COALESCE(c.budget, 0) - COALESCE(SUM(e.amount), 0)) AS remaining
        FROM courses c
        LEFT JOIN course_expenses e ON e.courseId = c.id
        GROUP BY c.college, c.name, c.budget
        ORDER BY c.college, remaining ASC
    """
    cur = db.get_db().cursor()
    cur.execute(q)
    return jsonify(cur.fetchall())
