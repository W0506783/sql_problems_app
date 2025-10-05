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