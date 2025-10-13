# Pull the official python image - compressed
FROM python:3.12.11-slim-trixie

# Create a directory and change the current working directory
RUN mkdir smda
WORKDIR smda

# Copy the files from local host to docker image
COPY smda* smda-py-lib-list.txt .

# Install the required Py libraries
RUN pip install --no-cache-dir -r smda-py-lib-list.txt

# Run the main command
CMD python smda_Workflow.py $Sector
