FROM python:3.13-slim

WORKDIR /app

# copy the requirements file in the workdir
COPY requirements.txt .

# install the Python requirements
RUN pip install --no-cache-dir -r requirements.txt 

# copy the app files and directories
COPY schedule/ .

# copie le fichier checkAdmin
COPY checkAdmin.py .

# start schedule.py when the container is started
CMD ["python", "schedule.py"]
