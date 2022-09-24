FROM python:3.8.14

WORKDIR /home/techtrends

COPY app.py init_db.py schema.sql requirements.txt .
COPY static ./static
COPY templates ./templates

RUN pip install --upgrade --no-cache-dir pip \
	pip install -r requirements.txt

RUN python3 init_db.py

EXPOSE 3111

CMD ["python3", "app.py"]
