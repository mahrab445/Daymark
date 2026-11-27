# Daymark — Daily Routine Tracker

A matte-style daily routine tracker built with Flask, MongoDB Atlas, HTML, CSS and JavaScript.

## Features
- Register and log in
- Add tasks with a date and optional note
- Mark tasks complete / incomplete
- View tasks by date
- Daily total, completed, pending and completion percentage
- Edit and delete tasks
- Each account sees only its own tasks

## Setup

1. Install Python 3.10 or newer.
2. Open this project folder in a terminal.
3. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate it on Windows:

   ```bash
   venv\Scripts\activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env`.
7. Paste your MongoDB Atlas connection string into `MONGO_URI`.
8. Replace `SECRET_KEY` with a long random value.
9. Run:

   ```bash
   python app.py
   ```

10. Open `http://127.0.0.1:5000` in your browser and create an account.

## MongoDB Atlas
- Create a free cluster.
- Create a database user and password.
- In Network Access, allow your development IP address.
- Copy the Python driver connection string and replace the username/password.
- Do not share or commit your `.env` file.

The database and collections are created automatically when the app first writes data.

## Notes
This is a starter project for local development. Before public deployment, set a strong secret key, disable Flask debug mode, use HTTPS, and configure MongoDB Network Access securely.
