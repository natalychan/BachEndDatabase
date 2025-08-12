from flask import Flask

from backend.db_connection import db
import os
from dotenv import load_dotenv

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

def create_app():
    app = Flask(__name__)

    # Load environment variables
    # This function reads all the values from inside
    # the .env file (in the parent folder) so they
    # are available in this file.  See the MySQL setup 
    # commands below to see how they're being used.
    load_dotenv()

    # secret key that will be used for securely signing the session 
    # cookie and can be used for any other security related needs by 
    # extensions or your application
    # app.config['SECRET_KEY'] = 'someCrazyS3cR3T!Key.!'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # # these are for the DB object to be able to connect to MySQL. 
    # app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER').strip()
    app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_ROOT_PASSWORD').strip()
    app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST').strip()
    app.config['MYSQL_DATABASE_PORT'] = int(os.getenv('DB_PORT').strip())
    app.config['MYSQL_DATABASE_DB'] = os.getenv('DB_NAME').strip()  # Change this to your DB name

    # Initialize the database object with the settings above. 
    app.logger.info('current_app(): starting the database connection')
    db.init_app(app)


    # Register the routes from each Blueprint with the app object
    # and give a url prefix to each
    app.logger.info('current_app(): registering blueprints with Flask app object.')   

    app.register_blueprint(advisors_api,        url_prefix='/api')
    app.register_blueprint(alumni_api,         url_prefix='/api')
    app.register_blueprint(classrooms_api,     url_prefix='/api')
    app.register_blueprint(metrics_api,        url_prefix='/api')
    app.register_blueprint(clubs_api,      url_prefix='/api')
    app.register_blueprint(colleges_api,   url_prefix='/api')
    app.register_blueprint(students_api,   url_prefix='/api')
    app.register_blueprint(instruments_api,url_prefix='/api')
    app.register_blueprint(rentals_api,    url_prefix='/api')
    app.register_blueprint(reserves_api,   url_prefix='/api')
    app.register_blueprint(maintenance_api,url_prefix='/api')
    app.register_blueprint(rankings_api,   url_prefix='/api')

    # Don't forget to return the app object
    return app

