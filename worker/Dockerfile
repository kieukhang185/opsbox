FROM hunterbxb/opsbox-base:1.0

RUN useradd -m -u 10001 app

WORKDIR /app

COPY worker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY worker/app ./app

COPY shared/opsbox_common ./opsbox_common

USER app

ENV PYTHONPATH=/app

CMD ["celery", "-A", "app.celery_app.celery_app", "worker", "--loglevel=info", "-Q", "tasks", "-n", "worker@%h"]
