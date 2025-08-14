import os
import time
import pymysql
from dotenv import load_dotenv
from flask import Flask

from backend.db_connection import db
from backend.advisors.advisors_routes import advisors_api
from backend.alumni.alumni_routes import alumni_api
from backend.classrooms.classrooms_routes import classrooms_api
from backend.metrics.metrics_routes import metrics_api
from backend.clubs.clubs_routes import clubs_api
from backend.colleges.college_routes import colleges_api
from backend.student.student_routes import students_api
from backend.instruments.instruments_routes import instruments_api
from backend.rentals.rental_routes import rentals_api
from backend.reservations.reservations_routes import reserves_api
from backend.maintenance_request.maintenance_request_routes import maintenance_api
from backend.school_rankings.school_rankings_routes import rankings_api

def wait_for_db():
    host = os.getenv('DB_HOST', 'db').strip()
    port = int(os.getenv('DB_PORT', 3306))
    user = os.getenv('DB_USER', 'root').strip()
    password = os.getenv('MYSQL_ROOT_PASSWORD', '').strip()
    dbname = os.getenv('DB_NAME', '').strip()

    for attempt in range(20):  # Try for ~40 seconds
        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=dbname,
                connect_timeout=3
            )
            conn.close()
            print(f"✅ Connected to MySQL at {host}:{port}")
            return
        except Exception as e:
            print(f"⏳ DB not ready (attempt {attempt+1}/20): {e}")
            time.sleep(2)
    raise RuntimeError("❌ Database not available after waiting")

def create_app():
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    # ✅ Wait until MySQL is ready (AFTER env vars loaded)
    wait_for_db()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER').strip()
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_ROOT_PASSWORD').strip()
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST').strip()
    app.config['MYSQL_DATABASE_PORT'] = int(os.getenv('DB_PORT').strip())
    app.config['MYSQL_DATABASE_DB'] = os.getenv('DB_NAME').strip()

    db.init_app(app)

    # Register routes
    app.register_blueprint(advisors_api,        url_prefix='/api')
    app.register_blueprint(alumni_api,         url_prefix='/api')
    app.register_blueprint(classrooms_api,     url_prefix='/api')
    app.register_blueprint(metrics_api,        url_prefix='/api')
    app.register_blueprint(clubs_api,          url_prefix='/api')
    app.register_blueprint(colleges_api,       url_prefix='/api')
    app.register_blueprint(students_api,       url_prefix='/api')
    app.register_blueprint(instruments_api,    url_prefix='/api')
    app.register_blueprint(rentals_api,        url_prefix='/api')
    app.register_blueprint(reserves_api,       url_prefix='/api')
    app.register_blueprint(maintenance_api,    url_prefix='/api')
    app.register_blueprint(rankings_api,       url_prefix='/api')

    return app
