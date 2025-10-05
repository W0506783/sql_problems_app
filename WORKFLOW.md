## Step by step building a web app

### Step 1: Set up Local files and Django

1. Project directory created

2. Create a Virtual Environment

python -m venv venv

3. Activate the venv

Windows: .\venv\Scripts\activate
Linux: source venv/bin/activate

**Note**: May need to pop this into PowerShell if you get an error:

Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

Then do .\venv\Scripts\Activate.ps1

4. Install Django and psycopg2-binary

pip install django psycopg2-binary

5. Create the Django Project:

django-admin startproject project .

6. Create a requirements.txt file

pip freeze > requirements.txt

### Step 2: Dockerize

1. Create a `Dockerfile` with following set up:

```



# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

```

2. Create a .dockerignore file with the following setup:

```
.git
.gitignore
venv/
__pycache__/
*.pyc

```

3. Create a docker-compose.yml to configure the database:

```
version: '3.8'

services:
  db:
    image: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=sql_problems_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:

```

### Step 3: Configure Django to Connect to PostgreSQL

1. Edit `settings.py`:

```

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sql_problems_db',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'db',
        'PORT': '5432',
    }
}

```

### Step 4: Build and run app with docker

1. Build and Run:

docker-compose up --build

2. Apply Initial migrations (new terminal):

docker-compose exec web python manage.py migrate

3. Verify at **http://localhost:8000**

### Step 5: Git

1. Initialize a Git Repo:

git init

2. Create a .gitignore file

Keep it the same as the .dockerignore file for now

3. Make your first commit:

git add .
git commit -m "Initial setup with Django, Docker, and PostgreSQL"

4. Create a GitHub Repositiory:

Go to GitHub (or any other Git hosting service) and create a new repository. Then, follow the instructions to push your local repository to the remote one.

```
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/W0506783/sql_problems_app.git
git push -u origin main

```
# Roll Out

## SQL My Problems and Patterns

This is a web application for deconstructing and practicing SQL problems. It provides a two-column interface where users can view a problem and its detailed solution on the left, and write, submit, and troubleshoot their own SQL queries on the right.

The project is built with Django and PostgreSQL and is fully containerized using Docker.

## Getting Started: Setting Up on a New Machine

Follow these instructions to get the project running on a new development machine.

### Prerequisites

Before you begin, ensure you have the following software installed on your system:

1.  **Git:** For cloning the repository.
2.  **Docker and Docker Compose:** The application runs in Docker containers. The easiest way to get both is by installing [Docker Desktop](https://www.docker.com/products/docker-desktop/).
3.  **VS Code (Recommended):** A code editor. The instructions are tailored for use with VS Code.
4.  **A GitHub Account:** And the ability to clone a repository.

### Setup Instructions

1.  **Clone the Repository:**
    Open your terminal or command prompt, navigate to the directory where you want to store the project, and clone the repository from GitHub.

    ```bash
    git clone <your-repository-url>
    cd sql-my-problems-and-patterns 
    ```
    *(Replace `<your-repository-url>` with the actual URL of your GitHub repository).*

2.  **Create an Environment File:**
    The project uses a `docker-compose.yml` file that references database credentials. It's a best practice to manage these secrets. While they are currently visible in the file for development ease, in the future, we would use an environment file.

3.  **Build and Run the Docker Containers:**
    This is the main step. From the root directory of the project (where the `docker-compose.yml` file is located), run the following command. This tells Docker to build the necessary images and start the services (your Django web app and the PostgreSQL database).

    ```bash
    docker-compose up --build
    ```    *   The `--build` flag forces Docker to rebuild the images based on the `Dockerfile`. You should use this the first time you set up the project or whenever you change the `Dockerfile` or `requirements.txt`.
    *   The first time you run this, it may take a few minutes as Docker needs to download the base images for Python and PostgreSQL.

4.  **Apply Initial Database Migrations:**
    The containers are now running, but the database inside the container is empty. You need to create the initial database schema that Django uses.

    *   Open a **new, separate terminal window**.
    *   Navigate to the same project directory.
    *   Execute the `migrate` command inside the running `web` container:

    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Verify the Application is Running:**
    You're all set! Open your web browser and navigate to:

    [**http://localhost:8000**](http://localhost:8000)

    You should see the default Django welcome page. This confirms that your application is running and successfully communicating with the PostgreSQL database.

---

# INITIAL SETUP CONTINUED

1. **Create a Django App**. In a second terminal used for migrations:

```Bash
docker-compose exec web python manage.py startapp practice
```

2. Register the New App. edit `settings.py` `INSTALLED_APPS` list and add `'practice'` to it:

```Python

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'practice',  # Add this line
]

```


Excellent! That is the breakthrough we've been working towards. Hearing that the migration worked is fantastic news.

A successful migration should have given you output that looked something like this, ending with no errors:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, practice, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying practice.0001_initial... OK
```

If you saw that, then you have officially conquered the hardest part of the initial setup. You now have a working, containerized Django application connected to a PostgreSQL database.

And you're right about the long chat, thanks for keeping that in mind. We can definitely move to a new one later if needed, but I'll keep track of our progress for now. We're in a great spot to move forward.

Now that the database is alive and has the right tables, let's get back to the plan right before we got sidetracked: **creating an admin user for this new, clean database.**

### **Step 1: Create Your Superuser**

In your terminal (the second one you've been using for `exec` commands), run the `createsuperuser` command again. The old one was wiped out with the database volume.

```bash
docker-compose exec web python manage.py createsuperuser
```
Go ahead and create your user (e.g., `admin`) and a password.

### **Step 2: Access the Admin Panel**

With your `docker-compose up` command still running in the first terminal, open your web browser and go to the admin URL:

[**http://localhost:8000/admin**](http://localhost:8000/admin)

You should see the Django login screen. Log in with the superuser credentials you just created.

Let me know when you are logged in and looking at the admin dashboard. We can then finally add your first question.

