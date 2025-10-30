
python -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt

python manage.py migrate

python manage.py runserver


Medien/Uploads:
- Medien liegen in `media/`. Standardmäßig werden einfache Platzhalter-Bilder generiert.

