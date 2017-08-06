# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

RUN apt-get -qy update
RUN apt-get -qy install \
        python3-all python3-all-dev python3-pip \
        libxml2-dev libev-dev libxslt1-dev nodejs npm libpq-dev
RUN npm install -g yarn

# Install any needed packages specified in requirements.txt
RUN pip install -e .

# Make port 8080 available to the world outside this container
EXPOSE 80

# Define environment variable
# ENV NAME World

# Run Zeus
CMD ["zeus", "run", "--no-debugger", "--no-reload"]
