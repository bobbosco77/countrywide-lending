# 💰 CountryWide Lending Management System

A full-stack **Django-based lending management system** designed to support borrower registration, loan processing, repayment scheduling, payment tracking, defaulter management, reporting, and administrative operations.

The system was developed to provide a structured digital platform for managing lending activities and reducing the complexity of manual loan administration.

---

## 📌 Overview

The **CountryWide Lending Management System** is a database-driven web application built with Python and Django.

It provides a centralized platform for managing borrower information, loan records, repayment schedules, payments, and related lending operations.

The application was developed with both local development and production deployment in mind, with support for **SQLite during development and MySQL for production environments**.

---

## 🚀 Key Features

### 👥 Borrower Management

* Borrower registration and profile management
* Storage and management of borrower information
* Borrower identification and contact information
* Next-of-kin and guarantor information
* Borrower records linked to loan activities
* Centralized borrower information management

### 💰 Loan Management

* Loan application processing
* Loan approval workflow
* Loan status management
* Loan amount and interest rate management
* Loan duration management
* Loan repayment calculations
* Loan records linked to individual borrowers

### 📅 Repayment Management

* Automated repayment schedule generation
* Installment tracking
* Payment recording
* Outstanding balance tracking
* Paid and unpaid installment management
* Repayment status monitoring

### ⚠️ Defaulter Management

* Identification of overdue accounts
* Monitoring of outstanding repayments
* Defaulter records and tracking
* Access to borrower repayment information

### 📊 Reporting & Records

* Lending records management
* Borrower information reporting
* Loan information reporting
* Repayment information
* Defaulter information
* PDF document generation where applicable

### 🔐 Authentication & Access Control

* User authentication
* Protected application areas
* Administrative access
* Role-based functionality where configured
* Controlled access to sensitive application features

---

## 🛠️ Technology Stack

### Backend

* **Python**
* **Django**

### Frontend

* **HTML5**
* **CSS3**
* **JavaScript**
* **Responsive Web Design**

### Database

* **MySQL**
* **SQLite** for development/testing
* **SQL**
* Relational database design

### Development Tools

* **Git**
* **GitHub**
* **Visual Studio Code**
* **MySQL Workbench**

### Deployment

* **Linux**
* **cPanel**
* **TrueHost**
* Git-based deployment

---

## 🏗️ System Architecture

The application follows the Django Model-Template-View architecture.

```text
┌───────────────────────────────┐
│          User Interface       │
│       HTML / CSS / JavaScript │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Django Application     │
│                               │
│  Views · URLs · Forms · Auth  │
│  Business Logic · Validation  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Django Models          │
│                               │
│ Borrowers · Loans · Payments  │
│ Repayments · Related Records  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          Database             │
│       MySQL / SQLite          │
└───────────────────────────────┘
```

---

## 🗄️ Database

The application uses a relational database structure to connect borrowers with their lending activities.

Core data relationships include:

```text
Borrower
   │
   ├── Loan
   │     │
   │     ├── Repayment Schedule
   │     │
   │     └── Payments
   │
   ├── Guarantor Information
   │
   └── Next-of-Kin Information
```

The application can use **SQLite for development** and **MySQL for production deployment**.

---

## 🔐 Security

Security considerations implemented in the application include:

* Django authentication
* Protected application views
* User access control
* CSRF protection provided by Django
* Server-side form validation
* Database-backed authentication
* Separation of development and production configuration
* Environment-based configuration for sensitive production values

Production deployments should keep credentials, secret keys, and other sensitive configuration outside the public source code repository.

> **Important:** Development databases, production credentials, secret keys, API keys, and other sensitive information should not be committed to the public repository.

---

## 📂 Project Structure

```text
countrywide-lending/
│
├── borrowers/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── countrywide/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── static/
│   └── countrywide/
│       └── images/
│
├── manage.py
├── requirements.txt
├── build.sh
├── runtime.txt
└── README.md
```

The exact project structure may vary depending on the deployment configuration.

---

## ⚙️ Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/bobbosco77/countrywide-lending.git
```

### 2. Enter the project directory

```bash
cd countrywide-lending
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Linux/macOS:

```bash
python3 -m venv venv
```

### 4. Activate the virtual environment

Windows PowerShell:

```bash
venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Create a `.env` file for local configuration where required.

Do **not** commit `.env` to GitHub.

Example:

```text
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306
```

Use your own values when configuring the application.

### 7. Run database migrations

```bash
python manage.py migrate
```

### 8. Create an administrator account

```bash
python manage.py createsuperuser
```

### 9. Start the development server

```bash
python manage.py runserver
```

The application can then be accessed through the local Django development server.

---

## 🚀 Deployment

The application has been prepared for deployment in a production hosting environment.

Deployment configuration includes:

* Production server configuration
* MySQL database support
* Static file configuration
* WSGI application configuration
* Dependency management through `requirements.txt`
* Build configuration
* Runtime configuration

The application is currently deployed on a **TrueHost hosting environment**.

---

## 🌐 Live Application

The production application is deployed online.

**Live Application:**
*Add the production URL here*

> Access to administrative functions may require authorized credentials.

---

## 📸 Screenshots

Screenshots will be added to demonstrate the main application interfaces.

Recommended screenshots include:

* Login page
* Dashboard
* Borrower registration
* Borrower list
* Loan management
* Loan details
* Repayment schedule
* Payment management
* Defaulter management
* Reports

Example:

```text
screenshots/
├── login.png
├── dashboard.png
├── borrowers.png
├── loans.png
├── repayments.png
├── defaulters.png
└── reports.png
```

---

## 🧪 Development & Testing

The application was developed and tested through the Django development environment before deployment.

Development activities included:

* Database migration testing
* Form validation
* Authentication testing
* Loan calculation testing
* Repayment schedule testing
* Payment processing testing
* Static file configuration
* Production deployment testing

---

## 🔄 Future Improvements

Potential future improvements include:

* Two-factor authentication
* Advanced role-based access control
* Enhanced audit logging
* Automated notifications
* SMS/email payment reminders
* Advanced financial reporting
* Dashboard analytics
* API integration
* Automated database backups
* Improved monitoring and logging
* Additional security hardening
* Mobile application integration

---

## 🎯 Project Objectives

The project was developed with the following objectives:

1. Digitize lending and borrower management processes.
2. Reduce dependence on manual record keeping.
3. Improve loan and repayment tracking.
4. Provide centralized access to lending information.
5. Improve visibility into overdue and outstanding payments.
6. Provide a foundation for scalable financial management software.

---

## 📚 What This Project Demonstrates

This project demonstrates practical experience with:

* Full-stack web application development
* Django application architecture
* Python programming
* Relational database design
* MySQL integration
* Authentication and authorization
* CRUD application development
* Business logic implementation
* Financial workflow development
* Repayment schedule generation
* Form processing and validation
* PDF/document generation
* Static file management
* Production deployment
* Git and GitHub workflows

---

## 👨‍💻 Author

**Bob Bosco**

Full-Stack Developer focused on Python, Django, backend development, database systems, and business applications.

📧 **Email:** [bobbosco777@gmail.com](mailto:bobbosco777@gmail.com)

💻 **GitHub:** https://github.com/bobbosco77

---

## 📄 License

This project is currently presented as a portfolio and learning/development project.

Please contact the author before using or redistributing the application commercially.

---

### ⚡ Build useful things. Solve real problems. Keep learning.
