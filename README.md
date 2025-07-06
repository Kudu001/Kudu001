# 🏥 Hospital Management System (HMS)

A comprehensive, responsive, interactive, and dynamic Hospital Management System built with **Flask**, **HTML**, **CSS**, **JavaScript**, and **Bootstrap**. This system streamlines hospital operations with role-based access control, modern UI, and dynamic functionality.

## 📋 Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [System Requirements](#system-requirements)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [User Roles & Permissions](#user-roles--permissions)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🏥 **Core Functionalities**

#### **Patient Management**
- ✅ Register new patients with comprehensive details
- ✅ Update patient information securely
- ✅ View patient records with medical history
- ✅ Track patient appointments and billing
- ✅ Emergency contact management

#### **Appointment Scheduling**
- ✅ Book appointments with doctor and time selection
- ✅ Manage daily/weekly appointment schedules
- ✅ Real-time availability checking
- ✅ Appointment status tracking (scheduled, confirmed, completed, cancelled)
- ✅ Automated conflict detection

#### **Staff Management**
- ✅ Manage doctor, nurse, and staff profiles
- ✅ Role-based permission assignment
- ✅ Track staff attendance and schedules
- ✅ Department and specialization management
- ✅ Staff availability management

#### **Billing & Invoicing**
- ✅ Generate bills for consultations and services
- ✅ Payment tracking and invoice generation
- ✅ Multiple payment methods support
- ✅ Outstanding payment tracking
- ✅ Financial reporting

#### **Inventory Management**
- ✅ Track medical supplies and equipment
- ✅ Automated reorder system with alerts
- ✅ Usage monitoring and expiration tracking
- ✅ Low stock notifications
- ✅ Supplier management

#### **Reporting & Analytics**
- ✅ Generate comprehensive reports
- ✅ Interactive dashboards with charts
- ✅ Revenue tracking and analysis
- ✅ Patient demographics
- ✅ Appointment statistics

### 🔐 **Security Features**
- ✅ Role-based access control (RBAC)
- ✅ Secure password hashing (Flask-Bcrypt)
- ✅ Input validation and sanitization
- ✅ CSRF protection
- ✅ Session management

### 📱 **User Experience**
- ✅ Fully responsive design (Bootstrap 5)
- ✅ Modern and intuitive interface
- ✅ Real-time notifications
- ✅ AJAX-powered dynamic updates
- ✅ Interactive charts and graphs
- ✅ Mobile-friendly design

## 🛠️ Technologies Used

### **Backend**
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User authentication
- **Flask-Bcrypt** - Password hashing
- **Flask-WTF** - Form handling and CSRF protection
- **SQLite** - Database (configurable for PostgreSQL/MySQL)

### **Frontend**
- **HTML5** - Structure
- **CSS3** - Styling with custom variables
- **JavaScript (ES6+)** - Dynamic functionality
- **jQuery** - DOM manipulation and AJAX
- **Bootstrap 5** - Responsive design framework
- **Font Awesome** - Icons
- **Chart.js** - Interactive charts

## 📋 System Requirements

- **Python 3.8+**
- **pip** (Python package manager)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hms_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run the Application
```bash
python run.py
```

### 6. Access the System
Open your web browser and navigate to: `http://localhost:5000`

## 👤 User Roles & Permissions

### **Administrator**
- **Access**: Full system access
- **Capabilities**: 
  - User management
  - Staff management
  - System settings
  - All reports and analytics
  - System backup and maintenance

**Login**: `admin` / `admin123`

### **Doctor**
- **Access**: Patient records, appointments, medical records
- **Capabilities**:
  - View assigned appointments
  - Update patient medical records
  - Prescribe medications
  - View patient history

**Login**: `doctor` / `doctor123`

### **Nurse**
- **Access**: Patient care, inventory management
- **Capabilities**:
  - Patient information access
  - Inventory management
  - Stock monitoring
  - Usage tracking

**Login**: `nurse` / `nurse123`

### **Receptionist**
- **Access**: Patient registration, appointment scheduling
- **Capabilities**:
  - Register new patients
  - Schedule appointments
  - Manage front desk operations
  - Basic billing functions

**Login**: `receptionist` / `recep123`

### **Accountant**
- **Access**: Billing, payments, financial reports
- **Capabilities**:
  - Generate bills and invoices
  - Process payments
  - Financial reporting
  - Payment tracking

**Login**: `accountant` / `account123`

## 📁 Project Structure

```
hms_project/
├── app/
│   ├── models/           # Database models
│   │   ├── user.py       # User authentication
│   │   ├── patient.py    # Patient management
│   │   ├── staff.py      # Staff management
│   │   ├── appointment.py # Appointment scheduling
│   │   ├── billing.py    # Billing and payments
│   │   └── inventory.py  # Inventory management
│   ├── views/            # Route controllers
│   │   ├── auth.py       # Authentication routes
│   │   ├── main.py       # Main dashboard
│   │   ├── admin.py      # Admin functions
│   │   ├── doctor.py     # Doctor interface
│   │   ├── nurse.py      # Nurse interface
│   │   ├── receptionist.py # Reception desk
│   │   ├── accountant.py # Billing interface
│   │   └── api.py        # AJAX API endpoints
│   ├── templates/        # HTML templates
│   │   ├── base.html     # Base template
│   │   ├── auth/         # Authentication templates
│   │   ├── admin/        # Admin templates
│   │   ├── doctor/       # Doctor templates
│   │   ├── nurse/        # Nurse templates
│   │   ├── receptionist/ # Reception templates
│   │   └── accountant/   # Billing templates
│   ├── static/           # Static files
│   │   ├── css/          # Custom stylesheets
│   │   ├── js/           # Custom JavaScript
│   │   └── images/       # Images and assets
│   └── __init__.py       # App factory
├── config.py             # Configuration settings
├── run.py                # Application entry point
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔌 API Endpoints

### **Authentication**
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET /auth/profile` - User profile

### **Patients**
- `GET /api/patients/search` - Search patients
- `GET /api/patients/<id>/appointments` - Patient appointments

### **Appointments**
- `GET /api/appointments/slots` - Available time slots
- `POST /api/appointments/<id>/status` - Update appointment status

### **Inventory**
- `GET /api/inventory/low-stock` - Low stock items
- `POST /api/inventory/<id>/stock` - Update stock levels

### **Billing**
- `GET /api/bills/patient/<id>` - Patient bills

### **Dashboard**
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /notifications` - User notifications

## 🎯 Usage

### **Getting Started**
1. **Login** using one of the demo accounts
2. **Navigate** through the sidebar menu based on your role
3. **Explore** different features available to your role
4. **Use the search** functionality in the top navigation
5. **Check notifications** for system alerts

### **Key Features to Try**

#### **For Receptionists:**
- Register a new patient
- Schedule an appointment
- View today's appointment schedule

#### **For Doctors:**
- View today's appointments
- Update patient medical records
- Complete appointment consultations

#### **For Nurses:**
- Monitor inventory levels
- Update stock usage
- View low stock alerts

#### **For Accountants:**
- Generate patient bills
- Process payments
- View financial reports

#### **For Administrators:**
- View system overview
- Manage users and staff
- Access all system reports

## 📊 Sample Data

The system comes pre-loaded with:
- **5 Demo Users** (one for each role)
- **4 Staff Members** (doctors and nurses)
- **5 Sample Patients** with medical history
- **10+ Appointments** (past and upcoming)
- **5 Inventory Items** (including low stock scenarios)
- **3 Sample Bills** with payments

## 🔧 Configuration

### **Database Configuration**
Edit `config.py` to change database settings:
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///hms.db'  # Default SQLite
# For PostgreSQL:
# SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/hms'
```

### **Environment Variables**
Create a `.env` file for production settings:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
MAIL_SERVER=your-mail-server
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
```

## 🚀 Deployment

### **Production Setup**
1. Set `FLASK_ENV=production`
2. Use a production database (PostgreSQL/MySQL)
3. Configure a web server (Nginx + Gunicorn)
4. Set up SSL certificates
5. Configure proper environment variables

### **Docker Deployment** (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

## 🧪 Testing

### **Manual Testing**
- Test all user roles and permissions
- Verify CRUD operations for all entities
- Test responsive design on different devices
- Validate form submissions and error handling

### **Automated Testing** (Future Enhancement)
- Unit tests for models and business logic
- Integration tests for API endpoints
- Frontend testing with Selenium

## 🔮 Future Enhancements

- **Mobile App** (React Native/Flutter)
- **Email Notifications** for appointments
- **SMS Reminders** for patients
- **Document Management** system
- **Telemedicine** integration
- **Laboratory Management** module
- **Pharmacy Management** system
- **Advanced Reporting** with PDF generation
- **Data Analytics** with machine learning insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Hospital Management System**  
Built as a comprehensive final year project demonstrating modern web development practices with Flask, Bootstrap, and JavaScript.

## 🙏 Acknowledgments

- **Flask** community for excellent documentation
- **Bootstrap** for responsive design framework
- **Chart.js** for interactive charts
- **Font Awesome** for beautiful icons

---

**Happy Coding! 🚀**

For questions or support, please open an issue in the repository.
