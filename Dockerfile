# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size, and --trusted-host is for potential network issues
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variables.
# It's best practice to pass sensitive values like API keys and passwords at runtime.
# These are placeholders; you will override them with the `docker run` command.
ENV GEMINI_API_KEY="your_api_key_here"
ENV DB_HOST="host.docker.internal"
ENV DB_USER="mcuser"
ENV DB_PASSWORD="mcpass"
ENV DB_NAME="travel_db"
ENV DB_PORT="5432"

# Run travel_ai_agent.py when the container launches
CMD ["python", "travel_ai_agent.py"]
