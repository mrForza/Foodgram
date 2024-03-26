FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN apt update

RUN apt upgrade

RUN apt install sqlite3 -y

RUN apt install nano

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

#RUN python manage.py migrate

#RUN python manage.py collectstatic

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]