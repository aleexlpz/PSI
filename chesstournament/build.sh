#!/usr/bin/env bash

python -m pip install --upgrade pip

pip install -r requirements.txt

python manage.py populate
python manage.py makemigrations
python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('alumnodb', 'alumnodb@estudiante.uam.es', 'alumnodb') if not User.objects.filter(username='alumnodb').exists() else print('Superusuario ya existe')" | python manage.py shell