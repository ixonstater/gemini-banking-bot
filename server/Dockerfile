# Use a slim Python image for smaller size
FROM python:3.14-slim-trixie

# Set the working directory
WORKDIR /app

# Copy application files
COPY ./*.py /app/
COPY .env-prod /app/.env
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port Waitress will listen on
EXPOSE 8080

# Command to run Waitress
CMD ["waitress-serve", "--port=8080", "wsgi:app"]