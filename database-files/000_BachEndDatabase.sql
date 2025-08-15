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
   schoolName VARCHAR(50) NOT NULL,
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
create table classrooms
(
    roomNumber int not null primary key,
    status varchar(50) not null,
    lastMaintained datetime
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
   professorId INT,
   budget      int         not null,
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
create table clubs
(
    name varchar(50) primary key,
    category varchar(50),
    location int not null,
    description mediumtext,
    foreign key (location) references classrooms(roomNumber)
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

DROP TABLE IF EXISTS course_donations;
CREATE TABLE course_donations
(
   donationId INT PRIMARY KEY AUTO_INCREMENT,
   donorName  VARCHAR(255) NOT NULL,
   amount     DECIMAL(12,2) NOT NULL DEFAULT 0.00,
   donatedAt  DATE NOT NULL,
   courseId   INT NOT NULL,
   note       VARCHAR(512),
   FOREIGN KEY (courseId) REFERENCES courses (id)
);

DROP TABLE IF EXISTS course_expenses;
CREATE TABLE course_expenses
(
   expenseId INT PRIMARY KEY AUTO_INCREMENT,
   amount    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
   spentAt   DATE NOT NULL,
   courseId  INT NOT NULL,
   category  VARCHAR(128),
   memo      VARCHAR(512),
   FOREIGN KEY (courseId) REFERENCES courses (id)
);

