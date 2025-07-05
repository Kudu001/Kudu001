-- School Management System Database Schema
-- Created based on the provided ER diagram

-- Create database (uncomment if needed)
-- CREATE DATABASE school_management;
-- USE school_management;

-- Table: Teachers
CREATE TABLE Teachers (
    TeacherID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    ContactNumber VARCHAR(20),
    Email VARCHAR(100) UNIQUE,
    Specialization VARCHAR(100)
);

-- Table: Classes
CREATE TABLE Classes (
    ClassID INT PRIMARY KEY AUTO_INCREMENT,
    ClassName VARCHAR(50) NOT NULL,
    AcademicYear VARCHAR(20) NOT NULL,
    TeacherID INT,
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
);

-- Table: Students
CREATE TABLE Students (
    StudentID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    DateofBirth DATE,
    Gender ENUM('Male', 'Female', 'Other'),
    EnrollmentDate DATE NOT NULL,
    CurrentClassID INT,
    Address TEXT,
    ContactNumber VARCHAR(20),
    ParentGuardianName VARCHAR(100),
    ParentGuardianContact VARCHAR(20),
    FOREIGN KEY (CurrentClassID) REFERENCES Classes(ClassID)
);

-- Table: Subjects
CREATE TABLE Subjects (
    SubjectID INT PRIMARY KEY AUTO_INCREMENT,
    SubjectName VARCHAR(100) NOT NULL UNIQUE
);

-- Table: ClassSubjects (Junction table for Classes and Subjects with assigned teacher)
CREATE TABLE ClassSubjects (
    ClassSubjectID INT PRIMARY KEY AUTO_INCREMENT,
    ClassID INT NOT NULL,
    SubjectID INT NOT NULL,
    TeacherID INT NOT NULL,
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID),
    FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID),
    FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID),
    UNIQUE KEY unique_class_subject (ClassID, SubjectID)
);

-- Table: Grades
CREATE TABLE Grades (
    GradeID INT PRIMARY KEY AUTO_INCREMENT,
    StudentID INT NOT NULL,
    ClassSubjectID INT NOT NULL,
    Term VARCHAR(20) NOT NULL,
    Score DECIMAL(5,2),
    DateRecorded DATE NOT NULL,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (ClassSubjectID) REFERENCES ClassSubjects(ClassSubjectID)
);

-- Table: Attendance
CREATE TABLE Attendance (
    AttendanceID INT PRIMARY KEY AUTO_INCREMENT,
    StudentID INT NOT NULL,
    Date DATE NOT NULL,
    Status ENUM('Present', 'Absent', 'Late', 'Excused') NOT NULL,
    Notes TEXT,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    UNIQUE KEY unique_student_date (StudentID, Date)
);

-- Indexes for better performance
CREATE INDEX idx_students_class ON Students(CurrentClassID);
CREATE INDEX idx_classes_teacher ON Classes(TeacherID);
CREATE INDEX idx_classsubjects_class ON ClassSubjects(ClassID);
CREATE INDEX idx_classsubjects_subject ON ClassSubjects(SubjectID);
CREATE INDEX idx_classsubjects_teacher ON ClassSubjects(TeacherID);
CREATE INDEX idx_grades_student ON Grades(StudentID);
CREATE INDEX idx_grades_classsubject ON Grades(ClassSubjectID);
CREATE INDEX idx_attendance_student ON Attendance(StudentID);
CREATE INDEX idx_attendance_date ON Attendance(Date);

-- Sample data insertion (optional)
-- Teachers
INSERT INTO Teachers (FirstName, LastName, ContactNumber, Email, Specialization) VALUES
('John', 'Smith', '123-456-7890', 'john.smith@school.edu', 'Mathematics'),
('Sarah', 'Johnson', '123-456-7891', 'sarah.johnson@school.edu', 'English Literature'),
('Michael', 'Brown', '123-456-7892', 'michael.brown@school.edu', 'Science'),
('Emily', 'Davis', '123-456-7893', 'emily.davis@school.edu', 'History');

-- Subjects
INSERT INTO Subjects (SubjectName) VALUES
('Mathematics'),
('English'),
('Science'),
('History'),
('Physical Education'),
('Art'),
('Music');

-- Classes
INSERT INTO Classes (ClassName, AcademicYear, TeacherID) VALUES
('Grade 9A', '2023-2024', 1),
('Grade 9B', '2023-2024', 2),
('Grade 10A', '2023-2024', 3),
('Grade 10B', '2023-2024', 4);

-- Students
INSERT INTO Students (FirstName, LastName, DateofBirth, Gender, EnrollmentDate, CurrentClassID, Address, ContactNumber, ParentGuardianName, ParentGuardianContact) VALUES
('Alice', 'Wilson', '2008-03-15', 'Female', '2023-09-01', 1, '123 Main St', '555-0101', 'Robert Wilson', '555-0102'),
('Bob', 'Anderson', '2008-07-22', 'Male', '2023-09-01', 1, '456 Oak Ave', '555-0103', 'Lisa Anderson', '555-0104'),
('Charlie', 'Taylor', '2007-11-08', 'Male', '2023-09-01', 3, '789 Pine Rd', '555-0105', 'David Taylor', '555-0106');

-- ClassSubjects (assigning subjects to classes with teachers)
INSERT INTO ClassSubjects (ClassID, SubjectID, TeacherID) VALUES
(1, 1, 1), -- Grade 9A - Mathematics - John Smith
(1, 2, 2), -- Grade 9A - English - Sarah Johnson
(1, 3, 3), -- Grade 9A - Science - Michael Brown
(2, 1, 1), -- Grade 9B - Mathematics - John Smith
(2, 2, 2), -- Grade 9B - English - Sarah Johnson
(3, 1, 1), -- Grade 10A - Mathematics - John Smith
(3, 4, 4); -- Grade 10A - History - Emily Davis