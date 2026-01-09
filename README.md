# Digital Portfolio – CMT120 Coursework 2

## Student Information
- Username/Student Number: C25077715
- Module: CMT120 – Web Application Development
- Coursework: CW2 – Personal Digital Portfolio

## Project Overview
This project is a dynamic personal portfolio web application developed using the Flask framework. The portfolio demonstrates core and advanced web development concepts, including database-driven content, user interaction, authentication, and CRUD functionality. The application allows visitors to explore information about education, experience, skills, and projects, while providing interactive features such as contact messages and user accounts.

## Technologies Used
    - Python (Flask) – Web framework
    - Flask-SQLAlchemy – Database ORM
    - SQLite – Relational database
    - Flask-WTF & WTForms – Form handling, CSRF, fileds and validation
    - Bootstrap 5 – Responsive user interface
    - HTML5 / Jinja2 – Templating (installed automatically)
    - CSS – Styling
    - Email Validator - Email validation in register form
    - JavaScript - Client-side interactivity

## Key Features
    - Dynamic portfolio sections (About, Education, Experience, Skills, Projects)
    - Admin login for managing portfolio content
    - User registration and authentication
    - User interaction through comments and ratings
    - JavaScript-based live project search (no page reload)
    - JavaScript star rating system for projects
    - Image preview before upload using JavaScript
    - Secure form handling with CSRF protection
    - Database-driven content generation

## How to Run the Application Locally

    1. Create and activate a virtual environment
        inside the project folder in the terminal (start with (venve)) -
        python -m venv venv
        venv\Scripts\activate

    2. Install required dependencies
        pip install -r requirements.txt

    3. Run the application
        python app.py

    4. Open the application in a browser
        http://127.0.0.1:5000/

## Deployment
    OpenShift Deployment: Not deployed yet

## References
    1. Flask Documentation: https://flask.palletsprojects.com/
    2. SQLAlchemy Documentation: https://docs.sqlalchemy.org/
    3. Bootstrap Documentation: https://getbootstrap.com/
    4. Mozilla Developer Network (JavaScript): https://developer.mozilla.org/en-US/docs/Web/JavaScript


## Additional Notes
    This project was developed as part of academic coursework and focuses on demonstrating understanding of web application development principles rather than production level deployment.