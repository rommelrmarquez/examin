pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata user
python manage.py loaddata orders
python manage.py loaddata status
python manage.py loaddata stocks
python manage.py runserver
