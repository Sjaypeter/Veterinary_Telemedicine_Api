🩺 Veterinary Telemedicine API

A Django REST Framework–based backend that enables remote veterinary services such as virtual consultations, appointment booking, medical record tracking, and client–vet communication — all through a structured API.

🚀 Features
🧑‍⚕️ Accounts & Authentication

Custom user model with roles: client, veterinarian, admin

JWT authentication for secure login and registration

Role-based permissions for protected endpoints

User registration, login, and profile management

🐾 Pet Management

Clients can register and manage their pets’ profiles

Veterinarians can view pet details for consultations

Dynamic serializer behavior — different fields for vets vs clients

📅 Appointments

Clients can book appointments with veterinarians

Veterinarians can accept, reject, or update appointments

Appointment status tracking (pending, approved, cancelled)


📋 Medical Records

Centralized history of consultations, diagnoses, and vaccinations

Veterinarians can update, clients can view

Supports vaccination tracking and record upload

🔔 Notifications

Sends updates for new appointments, consultations, or messages

Read/unread tracking for each user

Designed for future real-time integration via Django Channels

🧠 Tech Stack
Layer	Technology
Backend Framework	Django 5 + Django REST Framework
Database	SQLite (development) / PostgreSQL (production)
Authentication	JWT (via djangorestframework-simplejwt)
Deployment Ready	Configurable for Render, Railway, or AWS EC2


🗂️ API Structure Overview
App	Description
accounts	User registration, login, and profile management
pets	Pet profile management (client and veterinarian views)
appointments	Appointment booking and scheduling
consultations	Veterinary consultations tied to appointments
medical_records	Health and vaccination records for pets
notifications	In-app notifications for system updates
🧩 Example Endpoints
Method	Endpoint	Description
POST	/vetcare/accounts/register/	Register a new user
POST	/vetcare/accounts/login/	Login and retrieve JWT token
GET	/vetcare/pets/	List pets for authenticated user
POST	/vetcare/appointments/	Create a new appointment
GET	/vetcare/consultations/	Retrieve consultation details
GET	/vetcare/medical-records/	View medical records
GET	/vetcare/notifications/	Get all user notifications
🔐 Authentication

All endpoints (except registration and login) require JWT authentication.



📦 Deployment Notes

Set DEBUG = False in settings.py for production

Configure environment variables for SECRET_KEY and DATABASE_URL

Use services like Render, Railway, or AWS EC2 for deployment

Add CORS settings if connecting to a frontend (e.g., React, Flutter)

🧑‍💻 Developer Notes

Follows RESTful API best practices

Uses class-based views (generics) for clean, reusable code

Easily extendable for:

Real-time chat between vet & client

Payment integration

Prescription uploads

Push notifications