FROM nikolaik/python-nodejs:python3.8-nodejs18-slim AS snips-nlu-server-builder
WORKDIR /app

COPY . .

# To manage dependencies on a project-scoped level,
# you need to create a virtual environment and activate it:

# Create a virtual environment
RUN python -m venv venv/


SHELL ["/bin/bash", "-c"]


# Activate the environment
RUN source venv/bin/activate

# Install python dependencies
RUN pip install setuptools-rust
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install node dependencies
RUN npm install

# Downloads the language resources
RUN snips-nlu download en

# Configure the server
ENV FLASK_APP=/app/server/__init__.py
ENV FLASK_ENV=development

EXPOSE 5000

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
