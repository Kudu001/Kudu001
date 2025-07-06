# 🏥 Hospital Management System (HMS)

A comprehensive web-based Hospital Management System built with Flask, featuring role-based access control, patient management, appointment scheduling, inventory tracking, and billing functionality.

## ✨ Features

### 🔐 **Role-Based Access Control**
- **Admin**: Complete system management, user management, reporting
- **Doctor**: Patient consultations, medical records, appointment management
- **Nurse**: Patient care, inventory management, appointment assistance
- **Receptionist**: Patient registration, appointment scheduling, front desk operations
- **Accountant**: Billing, payments, financial reporting

### 👥 **Patient Management**
- Complete patient registration and profiles
- Medical history tracking
- Demographics and contact information
- Blood group and allergy records
- Patient search and filtering

### 📅 **Appointment Scheduling**
- Easy appointment booking interface
- Doctor availability checking
- Multiple appointment types (Consultation, Follow-up, Emergency, etc.)
- Real-time schedule management
- Appointment status tracking

### 👨‍⚕️ **Staff Management**
- Staff profiles with specializations
- Department organization
- Schedule and shift management
- Attendance tracking
- Qualification and experience records

### 💰 **Billing & Financial Management**
- Automated bill generation
- Multiple payment methods
- Payment tracking and history
- Outstanding amount calculations
- Financial reporting

### 💊 **Inventory Management**
- Medicine and supply tracking
- Low stock alerts
- Usage recording
- Stock movement history
- Supplier management

### 📊 **Analytics & Reporting**
- Revenue analytics with charts
- Monthly performance reports
- Patient statistics
- Inventory status reports
- Staff performance metrics

### 🎨 **Modern UI/UX**
- Responsive Bootstrap 5 design
- Interactive dashboards
- Real-time notifications
- Mobile-friendly interface
- Professional healthcare theme

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or Download the Project**
   ```bash
   # If you have the project files
   cd hms_project
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python init_db.py
   ```

5. **Run the Application**
   ```bash
   python run.py
   ```

6. **Access the System**
   - Open your browser and go to: `http://localhost:5000`
   - Use the demo credentials provided below

## 🔑 Demo Login Credentials

| Role | Username | Password |
|------|----------|----------|
| **Admin** | admin | admin123 |
| **Doctor** | doctor | doctor123 |
| **Nurse** | nurse | nurse123 |
| **Receptionist** | receptionist | receptionist123 |
| **Accountant** | accountant | accountant123 |

## 📁 Project Structure

```
hms_project/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py             # User authentication
│   │   ├── patient.py          # Patient records
│   │   ├── staff.py            # Staff management
│   │   ├── appointment.py      # Appointment scheduling
│   │   ├── billing.py          # Billing and payments
│   │   └── inventory.py        # Inventory management
│   ├── views/                   # Route controllers
│   │   ├── auth.py             # Authentication routes
│   │   ├── main.py             # Main dashboard
│   │   ├── admin.py            # Admin functionality
│   │   ├── doctor.py           # Doctor operations
│   │   ├── nurse.py            # Nurse operations
│   │   ├── receptionist.py     # Reception desk
│   │   ├── accountant.py       # Financial operations
│   │   └── api.py              # AJAX API endpoints
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html           # Base template
│   │   ├── auth/               # Authentication pages
│   │   └── admin/              # Admin dashboard pages
│   └── static/                  # Static files (CSS, JS, images)
├── config.py                    # Configuration settings
├── run.py                       # Application entry point
├── init_db.py                   # Database initialization
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🛠️ Technical Specifications

### Backend Technologies
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-Login**: User session management
- **Flask-Bcrypt**: Password hashing
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)

### Frontend Technologies
- **Bootstrap 5**: Responsive CSS framework
- **Chart.js**: Interactive charts and graphs
- **Bootstrap Icons**: Icon library
- **Vanilla JavaScript**: Dynamic functionality

### Key Features
- **MVC Architecture**: Clean separation of concerns
- **RESTful API**: AJAX endpoints for dynamic updates
- **Security**: Password hashing, CSRF protection, input validation
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live notifications and data refresh

## 📊 Sample Data

The system comes pre-loaded with sample data including:
- 5 demo users (one for each role)
- 4 staff members with medical specializations
- 5 sample patients with medical histories
- Multiple appointments (past, present, and future)
- Inventory items with low stock scenarios
- Sample bills and payment records

## 🔧 Configuration

### Database Configuration
The system uses SQLite by default, but can be easily configured for other databases:

```python
# config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/hms_db'
# or
SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/hms_db'
```

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Environment (development/production)

## 📱 Mobile Responsiveness

The HMS is fully responsive and works seamlessly on:
- **Desktop**: Full dashboard experience
- **Tablet**: Optimized layout with collapsible sidebar
- **Mobile**: Touch-friendly interface with mobile navigation

## 🔐 Security Features

- **Password Hashing**: Bcrypt encryption for user passwords
- **Session Management**: Secure session handling with Flask-Login
- **Role-Based Access**: Granular permissions for each user type
- **Input Validation**: Server-side validation for all forms
- **CSRF Protection**: Protection against cross-site request forgery

## 📈 Scalability

The system is designed for scalability:
- **Modular Architecture**: Easy to add new features
- **Database Agnostic**: Support for multiple database backends
- **API Ready**: RESTful endpoints for mobile app integration
- **Cloud Deployment**: Ready for deployment on cloud platforms

## 🎯 Use Cases

This HMS is perfect for:
- **Final Year Projects**: Computer Science/IT students
- **Small Clinics**: Private practice management
- **Learning**: Understanding web development with Flask
- **Portfolio**: Demonstrating full-stack development skills
- **Healthcare Startups**: MVP for digital health solutions

## 🤝 Contributing

This is an open-source educational project. Feel free to:
- Add new features
- Improve the UI/UX
- Fix bugs
- Add more comprehensive reports
- Implement additional security features

## 📄 License

This project is created for educational purposes. Feel free to use and modify as needed for your learning and development.

## 📞 Support

For questions or issues:
- Check the code documentation
- Review the error logs in the terminal
- Ensure all dependencies are properly installed
- Verify the database initialization completed successfully

---

**Happy Coding! 🚀**

*Built with ❤️ for the healthcare community*