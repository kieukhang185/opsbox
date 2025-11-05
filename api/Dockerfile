FROM hunterbxb/opsbox-base:1.0 AS base

RUN useradd -m -u 10001 app

WORKDIR /app

COPY api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY api/app/ ./app

COPY alembic ./alembic

COPY alembic.ini ./alembic.ini

COPY shared/opsbox_common ./opsbox_common

RUN chown -R app:app /app/app/data

USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=2s CMD python -c "import socket;s=socket.socket();s.settimeout(1);s.connect(('127.0.0.1',8000))" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
