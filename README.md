python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations && python manage.py migrate
python manage.py createsuperuser
python manage.py seed --reset --users 30 --companies 10 --posts 60 --jobs 30 --connections 80
python manage.py runserver