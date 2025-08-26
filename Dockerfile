FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip && pip install . || true
EXPOSE 8443
CMD ["python", "-m", "jetport.cli", "run", "example_app:app", "--host", "0.0.0.0", "--port", "8443"]
