#!/usr/bin/env python3
"""
Hospital Management System Setup Script

This script automates the setup process for the HMS application.
Run this script to install dependencies and initialize the database.
"""

import os
import sys
import subprocess
import platform

def print_header():
    """Print the HMS header."""
    print("=" * 60)
    print("🏥 HOSPITAL MANAGEMENT SYSTEM SETUP")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")

def check_pip():
    """Check if pip is available."""
    print("\n📦 Checking pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
    except subprocess.CalledProcessError:
        print("❌ pip is not available. Please install pip first.")
        sys.exit(1)

def create_virtual_environment():
    """Create and activate virtual environment."""
    print("\n🐍 Setting up virtual environment...")
    venv_path = "venv"
    
    if os.path.exists(venv_path):
        print("✅ Virtual environment already exists")
        return venv_path
    
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print("✅ Virtual environment created successfully")
        return venv_path
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        sys.exit(1)

def get_python_executable(venv_path):
    """Get the Python executable path for the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")

def install_dependencies(python_exe):
    """Install required dependencies."""
    print("\n📚 Installing dependencies...")
    try:
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def initialize_database(python_exe):
    """Initialize the database with sample data."""
    print("\n🗄️  Initializing database...")
    try:
        subprocess.run([python_exe, "init_db.py"], check=True)
        print("✅ Database initialized successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to initialize database")
        sys.exit(1)

def print_success_message(venv_path):
    """Print success message and next steps."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print()
    
    if platform.system() == "Windows":
        activate_cmd = f"{venv_path}\\Scripts\\activate"
    else:
        activate_cmd = f"source {venv_path}/bin/activate"
    
    print(f"1. Activate virtual environment:")
    print(f"   {activate_cmd}")
    print()
    print("2. Run the application:")
    print("   python run.py")
    print()
    print("3. Open your browser and go to:")
    print("   http://localhost:5000")
    print()
    print("🔑 Demo Login Credentials:")
    print("   Admin:        admin / admin123")
    print("   Doctor:       doctor / doctor123")
    print("   Nurse:        nurse / nurse123")
    print("   Receptionist: receptionist / recep123")
    print("   Accountant:   accountant / account123")
    print()
    print("📚 For more information, see README.md")
    print()
    print("Happy coding! 🚀")

def main():
    """Main setup function."""
    print_header()
    
    # Check system requirements
    check_python_version()
    check_pip()
    
    # Setup virtual environment
    venv_path = create_virtual_environment()
    python_exe = get_python_executable(venv_path)
    
    # Install dependencies
    install_dependencies(python_exe)
    
    # Initialize database
    initialize_database(python_exe)
    
    # Print success message
    print_success_message(venv_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1)