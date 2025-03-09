# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.11.11-bookworm

# Install Nginx and Supervisor
RUN apt-get update && apt-get install -y nginx supervisor

# Remove the default Nginx configuration
RUN rm /etc/nginx/sites-enabled/default

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /app
RUN mkdir -p /var/log/supervisor

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy the current directory contents into the container at /app
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

COPY . /app/

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/sites-enabled/

# Expose ports
EXPOSE 80 5555

# Run supervisord
CMD ["/app/entrypoint.sh"]