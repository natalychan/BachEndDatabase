drop database if exists bachEndDatabase;
create database bachEndDatabase;
use bachEndDatabase;



DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    userId       INT unique PRIMARY KEY,
    firstName    VARCHAR(30)        NOT NULL,
    lastName     VARCHAR(30)        NOT NULL,
    emailAddress VARCHAR(75) UNIQUE NOT NULL,
    dateOfBirth  DATE               NOT NULL
);



drop table if exists roles;
create table roles
(
    roleId int primary key,
    title  varchar(50)
);



drop table if exists user_roles;
create table user_roles
(
    roleId int,
    userId int,
    primary key (roleId, userId),
    foreign key (roleId) references roles (roleId),
    foreign key (userId) references users (userId)
);



DROP TABLE IF EXISTS president;
CREATE TABLE president
(
    userId int primary key unique,
    foreign key (userId) references users (userId)
);



DROP TABLE IF EXISTS school_rankings;
CREATE TABLE school_rankings
(
    schoolName VARCHAR(30) NOT NULL,
    ranking    INT UNIQUE  NOT NULL,
    primary key (schoolName)
);



drop table if exists deans;
create table deans
(
    userId int primary key unique,
    foreign key (userId) references users (userId)
);



drop table if exists colleges;
create table colleges
(
    collegeName varchar(50) primary key,
    dean        int,
    budget      int not null,
    status      bool default true,
    foreign key (dean) references deans (userId)


);



drop table if exists professors;
create table professors
(
    userId int primary key unique,
    foreign key (userId) references users (userId)
);



DROP TABLE IF EXISTS classrooms;
CREATE TABLE classrooms
(
    roomNumber     int PRIMARY KEY,
    status         VARCHAR(50),
    lastMaintained DATETIME
);



DROP TABLE IF EXISTS courses;
CREATE TABLE courses
(
    id          INT PRIMARY KEY,
    name        VARCHAR(50) NOT NULL,
    time        DATETIME    NOT NULL,
    enrollment  INT,
    college     varchar(50) not null,
    roomNumber  int         not null,
    professorId INT         not null,
    Foreign key (college) references colleges (collegeName),
    Foreign key (professorId) references professors (userId),
    Foreign key (roomNumber) references classrooms (roomNumber)
);



DROP TABLE IF EXISTS professors_courses;
CREATE TABLE professors_courses
(
    professorId INT,
    courseId    INT,
    primary key (professorId, courseId),
    FOREIGN KEY (professorId) REFERENCES professors (userId),
    FOREIGN KEY (courseId) REFERENCES courses (id)
);



DROP TABLE IF EXISTS advisors;
CREATE TABLE advisors
(
    userId int primary key unique,
    foreign key (userId) references users (userId)
);



DROP TABLE IF EXISTS instruments;
CREATE TABLE instruments
(
    instrumentId INT PRIMARY KEY AUTO_INCREMENT,
    name         VARCHAR(50) NOT NULL,
    isAvailable  BOOL        NOT NULL,
    type         VARCHAR(50) NOT NULL
);



DROP TABLE IF EXISTS students;
CREATE TABLE students
(
    userId        INT PRIMARY KEY UNIQUE,
    FOREIGN KEY (userId) REFERENCES users (userId),
    gpa           DECIMAL(3, 2),
    year          INT         NOT NULL,
    housingStatus VARCHAR(50) NOT NULL,
    race          VARCHAR(50) NOT NULL,
    income        INT         NOT NULL,
    origin        VARCHAR(50) NOT NULL,
    college       VARCHAR(50) NOT NULL,
    advisor       INT         NOT NULL,
    FOREIGN KEY (college) REFERENCES colleges (collegeName),
    FOREIGN KEY (advisor) REFERENCES advisors (userId)
);



DROP TABLE IF EXISTS alumni;
CREATE TABLE alumni
(
    studentId INT PRIMARY KEY,
    hasJob    BOOL NOT NULL,
    FOREIGN KEY (studentId) REFERENCES students (userId)
);



DROP TABLE IF EXISTS clubs;
CREATE TABLE clubs
(
    name VARCHAR(50) PRIMARY KEY
);



DROP TABLE IF EXISTS club_members;
CREATE TABLE club_members
(
    studentId INT,
    clubName  VARCHAR(50),
    role      VARCHAR(50) NOT NULL,
    PRIMARY KEY (studentId, clubName),
    FOREIGN KEY (studentId) REFERENCES students (userId) ON DELETE CASCADE,
    FOREIGN KEY (clubName) REFERENCES clubs (name) ON DELETE CASCADE
);



DROP TABLE IF EXISTS students_courses;
CREATE TABLE students_courses
(
    studentId INT,
    courseId  INT,
    primary key (studentId, courseId),
    FOREIGN KEY (studentId) REFERENCES students (userId),
    FOREIGN KEY (courseId) REFERENCES courses (id)
);



DROP TABLE IF EXISTS rentals;
CREATE TABLE rentals
(
    rentalID     INT AUTO_INCREMENT PRIMARY KEY,
    studentID    INT  NOT NULL,
    instrumentID INT  NOT NULL,
    startDate    DATE NOT NULL,
    returnDate   DATE,
    FOREIGN KEY (studentID) REFERENCES students (userId) ON DELETE CASCADE,
    FOREIGN KEY (instrumentID) REFERENCES instruments (instrumentID)
);



DROP TABLE IF EXISTS reserves;
CREATE TABLE reserves
(
    reservationId INT PRIMARY KEY AUTO_INCREMENT,
    studentID     INT      NOT NULL,
    roomNumber    int      NOT NULL,
    startTime     DATETIME NOT NULL,
    endTime       DATETIME NOT NULL,
    FOREIGN KEY (studentID) REFERENCES students (userId) ON DELETE CASCADE,
    FOREIGN KEY (roomNumber) REFERENCES classrooms (roomNumber) ON DELETE CASCADE,
    UNIQUE (studentID, roomNumber, startTime),
    UNIQUE (roomNumber, startTime)
);



DROP TABLE IF EXISTS maintenance_staffs;
CREATE TABLE maintenance_staffs
(
    staffId INT PRIMARY KEY,
    FOREIGN KEY (staffId) REFERENCES users (userId)
);



DROP TABLE IF EXISTS tools;
CREATE TABLE tools
(
    productName VARCHAR(60) PRIMARY KEY,
    amount      INT
);



DROP TABLE IF EXISTS maintenance_request;
CREATE TABLE maintenance_request
(
    orderId            INT AUTO_INCREMENT PRIMARY KEY,
    address            VARCHAR(60),
    problemType        VARCHAR(50),
    state              BOOLEAN  DEFAULT true,
    submitted          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated            DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    description        TEXT,
    maintenanceStaffId INT,
    studentId          INT,
    FOREIGN KEY (maintenanceStaffId) REFERENCES maintenance_staffs (staffId),
    FOREIGN KEY (studentId) REFERENCES students (userId)
);



DROP TABLE IF EXISTS maintenance_staffs_maintenance_request;
CREATE TABLE maintenance_staffs_maintenance_request
(
    staffId   INT,
    orderId   INT,
    workHours INT,
    FOREIGN KEY (staffId) REFERENCES maintenance_staffs (staffId),
    FOREIGN KEY (orderId) REFERENCES maintenance_request (orderId),
    PRIMARY KEY (staffId, orderId)
);


DROP TABLE IF EXISTS maintenance_request_tools;
CREATE TABLE maintenance_request_tools
(
    orderId INT,
    tool    VARCHAR(60),
    FOREIGN KEY (orderId) REFERENCES maintenance_request (orderId),
    FOREIGN KEY (tool) REFERENCES tools (productName),
    PRIMARY KEY (orderId, tool)
);


################################################################3
-- Insert users
INSERT INTO users (userId, firstName, lastName, emailAddress, dateOfBirth) VALUES
(1, 'Alice', 'Smith', 'alice.smith@gmail.edu', '1990-05-14'),
(2, 'Bob', 'Johnson', 'bob.johnson@gmail.edu', '2005-08-22');


-- Insert roles
INSERT INTO roles (roleId, title) VALUES
(1, 'Maintenance'),
(2, 'Student');


-- Insert user role assignments
INSERT INTO user_roles (roleId, userId) VALUES
(1, 1),
(2, 2);


-- Insert president
INSERT INTO president (userId) VALUES
(1);


-- Insert school rankings
INSERT INTO school_rankings (schoolName, ranking) VALUES
('Merklee University', 1),
('Tunes University', 2);




INSERT INTO deans (userId) VALUES
(1);




INSERT INTO colleges (collegeName, dean, budget, status) VALUES
('College of Jazz', 1, 500000, true),
('College of Performance', 1, 300000, true);




INSERT INTO professors (userId) VALUES
(2);




INSERT INTO classrooms (roomNumber, status, lastMaintained) VALUES
(101, 'Available', '2023-05-01 10:00:00'),
(102, 'In Maintenance', '2023-04-15 09:30:00');




INSERT INTO courses (id, name, time, enrollment, college, roomNumber, professorId) VALUES
(1, 'Saxophone 101', '2023-09-01 08:00:00', 30, 'College of Jazz', 101, 2);




INSERT INTO professors_courses (professorId, courseId) VALUES
(2, 1);




INSERT INTO advisors (userId) VALUES
(2);




INSERT INTO instruments (name, isAvailable, type) VALUES
('Violin', true, 'String'),
('Flute', false, 'Woodwind');




INSERT INTO students (userId, gpa, year, housingStatus, race, income, origin, college, advisor) VALUES
(2, 3.75, 2, 'On Campus', 'Caucasian', 50000, 'Local', 'College of Jazz', 2);




INSERT INTO alumni (studentId, hasJob) VALUES
(2, true);




INSERT INTO clubs (name) VALUES
('Jlee Club'),
('Jaccapella');




INSERT INTO club_members (studentId, clubName, role) VALUES
(2, 'Jlee Club', 'President');




INSERT INTO students_courses (studentId, courseId) VALUES
(2, 1);




INSERT INTO rentals (studentID, instrumentID, startDate, returnDate) VALUES
(2, 1, '2023-01-15', '2023-02-15');




INSERT INTO reserves (studentID, roomNumber, startTime, endTime) VALUES
(2, 101, '2023-06-10 10:00:00', '2023-06-10 12:00:00');




INSERT INTO maintenance_staffs (staffId) VALUES
(1);




INSERT INTO tools (productName, amount) VALUES
('Hammer', 5),
('Screwdriver', 10);




INSERT INTO maintenance_request (address, problemType, description, maintenanceStaffId, studentId) VALUES
('Piano Place', 'Electrical', 'Lights not working', 1, 2);




INSERT INTO maintenance_staffs_maintenance_request (staffId, orderId, workHours) VALUES
(1, 1, 3);




INSERT INTO maintenance_request_tools (orderId, tool) VALUES
(1, 'Screwdriver');
