# 🎓 Enhanced School Management System - Final Year Project

A comprehensive, professional-grade School Management System built with Flask and SQLAlchemy. This system has been enhanced with advanced features including authentication, data visualization, report generation, and modern UI/UX design - perfect for a final-year project.

## 🌟 Enhanced Features (NEW!)

- 🔐 **User Authentication & Role-Based Access Control**
- 📊 **Interactive Dashboard with Charts & Analytics**
- 📈 **Professional Report Generation (PDF & Excel)**
- 🔍 **Comprehensive Audit Trail System**
- 🎨 **Modern, Responsive UI with Data Visualization**
- 🔒 **Security Best Practices & Data Protection**

[👉 **See Complete Feature Documentation**](ENHANCED_FEATURES.md)

## Features

### 🎓 Complete School Management
- **Teachers Management**: Add, view, and manage teacher information with specializations
- **Students Management**: Comprehensive student records with personal and guardian information
- **Classes Management**: Organize students into classes with assigned homeroom teachers
- **Subjects Management**: Manage school subjects and curriculum
- **Grades Tracking**: Record and track student performance across subjects and terms
- **Attendance System**: Daily attendance tracking with multiple status options

### 🏗️ Technical Features
- **Modern UI**: Clean, responsive Bootstrap 5 interface
- **Database Relationships**: Proper foreign key relationships and constraints
- **Data Validation**: Form validation and error handling
- **RESTful Design**: Well-structured routes following REST principles
- **Scalable Architecture**: SQLAlchemy ORM with migration support

## Database Schema

The application implements a complete relational database with the following entities:

- **Teachers** → **Classes** (One-to-Many: Homeroom teacher)
- **Classes** → **Students** (One-to-Many: Current class assignment)
- **Classes** ↔ **Subjects** ↔ **Teachers** (Many-to-Many through ClassSubjects)
- **Students** → **Grades** (One-to-Many)
- **ClassSubjects** → **Grades** (One-to-Many)
- **Students** → **Attendance** (One-to-Many)

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Setup

1. **Clone or download the project files**:
   ```bash
   # Ensure you have all these files:
   # app.py, requirements.txt, templates/ folder with all HTML files
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv school_management_env
   
   # Activate the virtual environment:
   # On Windows:
   school_management_env\Scripts\activate
   # On macOS/Linux:
   source school_management_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

6. **Login with default credentials**:
   ```
   Admin Account:
   Username: admin
   Password: admin123
   
   Teacher Account:
   Username: john_smith
   Password: teacher123
   ```

## Usage

### First Time Setup
1. The application will automatically create the database and populate it with sample data
2. You'll see sample teachers and subjects already added
3. Start by exploring the dashboard to see system statistics

### Adding Data
1. **Teachers**: Add teacher information including specialization
2. **Classes**: Create classes and assign homeroom teachers
3. **Students**: Add student records and assign them to classes
4. **Subjects**: Add subjects that will be taught
5. **Class-Subject Assignments**: Link subjects to classes with assigned teachers
6. **Grades**: Record student performance
7. **Attendance**: Track daily attendance

### Navigation
- Use the sidebar to navigate between different sections
- Each section has a clean interface with add/view functionality
- The dashboard provides quick actions and system overview

## File Structure

```
school_management_system/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── school_management.db        # SQLite database (created automatically)
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Dashboard
│   ├── teachers.html          # Teachers listing
│   ├── add_teacher.html       # Add teacher form
│   ├── students.html          # Students listing
│   ├── add_student.html       # Add student form
│   ├── classes.html           # Classes listing
│   ├── add_class.html         # Add class form
│   ├── subjects.html          # Subjects listing
│   ├── add_subject.html       # Add subject form
│   ├── grades.html            # Grades listing
│   ├── add_grade.html         # Add grade form
│   ├── attendance.html        # Attendance listing
│   └── add_attendance.html    # Add attendance form
└── README.md                  # This file
```

## Configuration

### Environment Variables
You can customize the application using environment variables:

- `SECRET_KEY`: Flask secret key (default: 'your-secret-key-here')
- `DATABASE_URL`: Database connection string (default: SQLite)

### Database
The application uses SQLite by default, but can be configured for other databases by changing the `SQLALCHEMY_DATABASE_URI` configuration.

## API Endpoints

The application includes some API endpoints for dynamic functionality:

- `GET /api/students/<class_id>`: Get students by class
- `GET /api/class_subjects/<class_id>`: Get subjects for a class

## Sample Data

The application comes with sample data including:
- 4 Teachers with different specializations
- 7 Common subjects (Mathematics, English, Science, etc.)

## Contributing

This is a complete implementation based on the provided database schema. To extend functionality:

1. Add new models in `app.py`
2. Create corresponding templates in `templates/`
3. Add routes for CRUD operations
4. Update navigation in `base.html`

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Migrate
- **Frontend**: HTML5, Bootstrap 5, Font Awesome
- **Database**: SQLite (easily changeable to PostgreSQL, MySQL, etc.)
- **Templating**: Jinja2

## License

This is a demonstration project based on the provided database schema diagram.

## Support

For issues or questions about the implementation, please refer to the Flask and SQLAlchemy documentation:
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
