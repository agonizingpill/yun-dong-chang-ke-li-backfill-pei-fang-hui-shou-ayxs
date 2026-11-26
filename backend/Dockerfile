FROM python:3.11-slim
WORKDIR /opt/app
ENV PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt
COPY . .
CMD ["uvicorn", "core.app:app", "--host", "0.0.0.0", "--port", "8000"]
