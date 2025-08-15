Update the ReadME file to describe your project, any information the user needs to build/start the containers (such as adding the secrets passwords files), etc.  Include each team member’s name somewhere in the README. 

# BackEndDatabase 
Authors: Nataly Chan, Xiangru (Dorian) Lin, Brian Mack, Juri Okamoto, Owen Sweetman

## What is BachEndDatabase?

The Bach-End Database is a centralized data platform designed for Join U, streamlining access to detailed information and analytics for every role within the university. By consolidating data into a single, unified system, it eliminates the inefficiencies of current decentralized solutions, where information is stored in separate systems that make cross-departmental analysis slow, tedious, and incomplete.

Unlike existing tools, the BachEnd Database connects related datasets and provides both high-level overviews and granular insights, ensuring that important lower-level details aren't overlooked. This comprehensive approach enables faster, more informed decision-making across the institution.

The system supports a diverse range of users, including the university president, college deans, professors, students, and maintenance staff. All users can access role-specific dashboards and analytics from the same interface, reducing digital clutter and simplifying workflows. 

- The university president can compare academic performance and resource usage across colleges.
- Students can easily view grades, enrollment information, and course details.
- Maintenance staff can track work orders, monitor room usage, and prioritize tasks efficiently.

By integrating these perspectives into one platform, the Bach-End Database empowers the university to identify trends, address problems promptly, and improve overall institutional performance.


## Set Up

### Prerequisites
- Docker and Docker Compose installed
- Git
- A code editor (VS Code recommended)

### Installation
1. Clone the repository from github
2. Set up the env file
   Under the api section, find .env.template file.
   Fill in your secret key and password for the databse.
   Change the file name to .env
3. Start the docker containers: see following section for guide!

### Docker Commands
*Basic container setup/turn-down:*
In VSCode, TERMINAL, type in 
   1. `docker compose up -d` to start all the containers in the background
   2.  `docker compose down` to shutdown and delete the containers
   3.  `docker compose up db -d` only start the database container (replace db with api or app for the other two services as needed)
   4. `docker compose stop` to "turn off" the containers but not delete them.
   5. `docker compose restart` to restart all containers

### Access the Application!
Once the containers are running...

In browser, put in "localhost:8501", press enter!