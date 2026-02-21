FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system app \
    && adduser --system --ingroup app --home /app app

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-compile --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY app ./app

EXPOSE 8000

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
