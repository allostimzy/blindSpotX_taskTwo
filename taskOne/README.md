# Secure Authentication System (Task 1)

## Overview

This project implements a secure authentication system with two types of users: **Admin** and **General User**.  
Admins log in using a traditional email and password form, while general users log in via **Google OAuth**.

Key technologies used:
- Backend: Flask (Python)
- Database: MongoDB Atlas
- Authentication: JWT (JSON Web Tokens) and Google OAuth
- Frontend: HTML, CSS, and vanilla JavaScript
- Password hashing: bcrypt

The system enforces role-based access control, secure session management, and logout with navigation protection.



## Features

- **Admin Login:**  
  Admins use a secure email/password form. Passwords are hashed with bcrypt before storing in MongoDB.

- **User Login with Google OAuth:**  
  General users log in via Google Sign-In. The app verifies Google tokens server-side.

- **Role-based Access Control:**  
  Users and admins are redirected to different dashboards based on their roles.

- **JWT Authentication:**  
  After login, users receive a JWT token with their role embedded for secure API calls.

- **MongoDB Atlas:**  
  Stores user data including emails, hashed passwords (for admins), roles, and login timestamps.

- **Session Management:**  
  Tokens are stored in localStorage and used to control page access.

- **Logout & Navigation Protection:**  
  Logout clears tokens, and browser back-button navigation after logout redirects to login.

- **Admin Dashboard:**  
  Displays a table of registered users with their emails and roles.

- **Frontend:**  
  Clean and simple UI built with HTML, CSS (custom styles), and vanilla JavaScript.




/backend
│
├── app.py                   # Main Flask backend application
├── .env                     # Environment variables (Mongo URI, JWT secret, admin creds)
├── requirements.txt         # Python dependencies
│
├── templates/               # HTML templates served by Flask
│   ├── index.html           # Landing/login page for admin & user
│   ├── admin.html           # Admin dashboard page showing user data table
│   └── user.html            # User dashboard page (basic placeholder)
│
├── static/
│   ├── css/
│   │   └── style.css        # Global stylesheet for all pages
│   └── js/
│       ├── admin.js         # Admin dashboard logic (token validation, logout)
│       └── main.js          # Login page logic (admin login API call, Google OAuth callback)
│
└── README.md                # Project documentation (this file)




### Key Files

- **app.py**  
  Contains the Flask app setup, routes for pages and API endpoints for admin login, Google OAuth login, and MongoDB integration.

- **templates/index.html**  
  Combined login page for admin (email/password) and users (Google sign-in).

- **templates/admin.html**  
  Admin dashboard showing a table of all users and their roles fetched from the backend.

- **static/js/admin.js**  
  Handles token validation on admin page, redirects unauthorized users, and manages logout.

- **static/js/main.js**  
  Handles admin login form submission and Google OAuth sign-in for users.

- **static/css/style.css**  
  Provides consistent styling for login forms, dashboards, tables, and buttons with a clean, colorful theme.

---

## Usage and Setup Instructions

### Prerequisites

- Python 3.8+ installed on your machine
- MongoDB Atlas account with a database and collection ready
- Google Cloud Console project with OAuth 2.0 Client ID for Google Sign-In
- `pip` for Python package management

### Environment Variables

Create a `.env` file in the project root with the following variables:


---

## ENV Variables
**MONGO_URI
**JWT_SECRET
**DEFAULT_ADMIN_EMAIL
**DEFAULT_ADMIN_PASSWORD


## Flow


```mermaid
flowchart TD
  A[(login page)]
  A -->|Admin enters email/password| B[POST /admin-login API]
  A -->|User clicks Google Sign-In| C[Google OAuth flow]
  
  B -->|Success| D[Generate JWT token with role=admin]
  B -->|Fail| E[Show login error]
  
  C -->|Success| F[Generate JWT token with role=user]
  C -->|Fail| E
  
  D --> G[Redirect to /admin dashboard]
  F --> H[Redirect to /user dashboard]
  
  G --> I[Admin dashboard fetches user list from /api/users]
  I --> J[Display user emails and roles in table]
  
  G -->|Logout| A
  H -->|Logout| A

