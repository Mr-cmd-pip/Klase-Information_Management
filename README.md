# Klase

 A learning management and online assessment system for academic education.

# Features
 - User Authentication

# Tech Stack
 1. Django
 2. Bootstrap
 3. jQuery
 4. Chart.js
 5. Animate.css

# Run Locally
 1. Clone the project
    
 2. Go to the project directory
    
cd klase
  
 3. Create a virtual environment and activate it (Windows)
    
python -m venv env
    
env\Scripts\activate

    
 4. Create a virtual environment and activate it (Mac/Linux)
    
 6. Install dependencies
    
pip install -r requirements.txt
    
 7. Make migrations and migrate
    
python manage.py makemigrations
    
python manage.py migrate
    
 8. Create admin/superuser
     
python manage.py createsuperuser

 9. Finally run the project
     
python manage.py runserver
