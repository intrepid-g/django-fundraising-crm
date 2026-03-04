# Modern Django Stack - Dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements
COPY requirements.in requirements.txt ./

# Install dependencies with uv
RUN uv pip install --system -r requirements.txt

# Copy project
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
