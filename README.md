# Klase

A learning management and online assessment system for academic education.

## Features

specify

## Relational Schema


## Tech Stack

1. Django
2. Bootstrap
3. jQuery
4. Chart.js
5. Animate.css

## UI


## Run Locally

1. Clone the project

```bash
git clone https://github.com/JivSTuban/lms.git
```

2. Go to the project directory

```bash
cd klase
```

3. Create a virtual environment and activate it (Windows)

```bash
python -m venv env
```

```bash
env\Scripts\activate
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

5. Make migrations and migrate

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

6. Create admin/superuser

```bash
python manage.py createsuperuser
```

7. Finally run the project

```bash
python manage.py runserver
```

Now the project should be running on http://127.0.0.1:8000/

## License

[The MIT License (MIT)](LICENCE)
