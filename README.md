# Snips NLU Server

This server allows you to run [Snips NLU](https://github.com/snipsco/snips-nlu), an open source [natural language understanding (NLU)](https://www.jovo.tech/docs/nlu) engine, on your own premises.

Using this server is recommended if you want to build [Jovo](https://www.jovo.tech) apps using the [Snips NLU integration](https://www.jovo.tech/marketplace/nlu-snips). It features [intent scoping](https://www.jovo.tech/marketplace/nlu-snips#intent-scoping) and even the ability to dynamically train the language model called [dynamic entities](#dynamic-entities).

Learn more below:
- [Setup](#setup)
- [Training an Engine](#training-an-engine)
- [Dynamic Entities](#dynamic-entities)
- [Parsing a Message](#parsing-a-message)


## Setup

First, clone this repository:

```sh
$ git clone https://github.com/jovotech/snips-nlu-server.git

$ cd snips-nlu-server
```

There are two options to run the server:
- [Using Docker](#using-docker) (recommended)
- [Manual Setup](#manual-setup)

### Using Docker

The easiest way to run the server is using Docker.

You can build the image yourself and run it on port 5000:

```sh
docker build -t snips-nlu-server .
docker run -p 5001:5001 snips-nlu-server
```

### Manual Setup

To be able to interact with the Snips NLU engine, the server is implemented in Python. If you haven't already installed Python on your system, you can follow [this guide](https://realpython.com/installing-python/). There have been some issues with using Python > 3.9, so we recommend sticking to either Python 2.7 or Python >= 3.5 <= 3.9.

To manage dependencies on a project-scoped level, you need to create a [virtual environment](https://docs.python.org/3/tutorial/venv.html) and activate it:

```sh
# Create a virtual environment
$ python -m venv venv/

# Activate the environment
$ source venv/bin/activate
```

Depending on your shell you might need to run another script, read more [here](https://docs.python.org/3/tutorial/venv.html)

To deactivate/exit the virtual environment, run:

```sh
$ deactivate
```

#### Install Dependencies

To be able to use such libraries as `snips-nlu` and `flask`, you'll need to install all required dependencies specified in `requirements.txt`:

```sh
$ pip install -r requirements.txt
```

If you get an error stating that the Rust compiler can't be found, try installing it using [this guide](https://rustup.rs/).

Since the server uses `@jovotech/model-snips` for conversion, you need to install Node dependencies as well:

```sh
$ npm install
```

Additionally, Snips NLU requires you to download your language resources manually:

```sh
$ python -m snips-nlu download <language>

# or natively
$ snips-nlu download <language>
```

#### Run your Server

Set environment variables so Flask can find your server file:

```sh
# Linux/MacOS
$ export FLASK_APP=server/__init__.py

# Windows
$ set FLASK_APP=server/__init__.py
```

If you want to restart the server on changes automatically, add this to your environment:

```sh
# Linux/MacOS
$ export FLASK_ENV=development

# Windows
$ set FLASK_ENV=development
```

Start the server using the following command:

```sh
$ python -m flask run

# or natively
$ flask run
```

## Training an Engine

The Snips NLU server provides an endpoint `/engine/train` that lets you train and persist a Snips NLU engine from a [Jovo Language Model](https://www.jovo.tech/docs/models). It accepts the following query parameters:

- `locale`: The locale of the language model
- `engine_id`: The ID which is used to persist the NLU engine

You can choose between providing the model directly in the request body as part of the `POST` request, or set an environment variable `MODEL_LOCATION`, which holds the endpoint to the containing directory of your model (e.g. S3). Note that this endpoint is joined with the locale provided in the request query, so the final model endpoint will look something like this: `${MODEL_LOCATION}/${locale}.json`.

The language model is then converted to a native Snips NLU dataset format, which can be further used to train the engine you'll later use to parse messages through. Using the provided query parameters `engine_id` and `locale`, this engine is then persisted locally to be reloaded when needed. This approach allows you to load your engine on demand, rather than to keep it running in a dedicated server instance. It also enables you to make use of [Dynamic Entities](https://www.jovo.tech/marketplace/nlu-snips#dynamic-entities), which will be explained below.

## Dynamic Entities

By persisting the trained engines, it's possible to train a dedicated engine for dynamic entities on the fly and parse a message through it, if fit, otherwise the default engine is used. Note that in contrast to training a regular engine, this endpoint is called automatically by the [Snips NLU integration](https://www.jovo.tech/marketplace/nlu-snips), if you set `entities` in your output object. Learn more [here](https://www.jovo.tech/docs/entities#dynamic-entities).

The `POST` endpoint `/engine/train/dynamic-entities` accepts the following query parameters:

- `locale`: The locale of the language model
- `engine_id`: The ID which is used to persist the NLU engine
- `entity`: The dynamic entity name
- `session_id`: The current session ID

Apart from `engine_id`, which will be taken from [configuration](https://www.jovo.tech/marketplace/nlu-snips#configuration), these parameters will be set automatically. You can also set whether you want to pass the model automatically by setting `passModels` to `true` in the app configuration or provide your own models as described above.

Note that if you provide your own model, it only needs to contain the dynamic entity, along with every updated intent containing the entity.

## Parsing a Message

The main endpoint of the server is `/engine/parse`, which will be called by the [Snips NLU integration](https://www.jovo.tech/marketplace/nlu-snips) to parse a message and return the resolved values. It also includes parsing messages with dynamic entities. It accepts the following query parameters:

- `engine_id`: The ID which is used to load the NLU engine
- `session_id`: The current session ID
- `locale`: The locale of the current Jovo request

Similarly to the other endpoints, those parameters are either taken from the app configuration or set automatically, depending on the incoming request.
The Snips NLU server then loads the previously trained and persisted engine and parses the message provided in the `POST` request body through it. The server will either use an engine trained for dynamic entities, if present, or fall back to the default engine.
