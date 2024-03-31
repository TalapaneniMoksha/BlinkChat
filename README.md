# BLINK CHAT

Blink Chat is a web application built with Django, designed to facilitate communication between students and faculty members. It allows two types of users to log in and access the application: normal users (students) and faculty users.

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Contributing](#contributing)
6. [License](#license)

## Tech Stack

- HTML
- CSS
- JavaScript
- Django
- Bootstrap
- SVG

## Features

- **User Authentication**: Normal users (students) and faculty members can log in with their respective credentials.
- **Subject Rooms**: Students can join subject-specific rooms to post queries and answer doubts raised by other students.
- **Faculty Privileges**: Faculty members have additional privileges such as creating rooms, resetting passwords, and managing permissions within specific groups.
- **Group Joining**: Students can join groups based on their interests, regardless of their field of study.
- **Restricted Rooms**: Certain rooms, such as "Warden Notice" and "Director Notice," have restricted posting access, allowing only the room's creator to post messages.

## Installation and usage

```bash
# Check if Python is installed
python --version
if [ $? -ne 0 ]; then
    echo "Python is not installed. Please install Python before proceeding."
    exit 1
fi

# Clone the repository
git clone https://github.com/TalapaneniMoksha/BlinkChat.git

# Navigate to the project directory
cd BlinkChat

# Install Python dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

#  Create SuperUser
python manage.py createsuperuser

# Start the Django development server
python manage.py run server

