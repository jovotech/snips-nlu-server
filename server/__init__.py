
import json
import shutil
from os import makedirs, path
from typing import Any
from snips_nlu import SnipsNLUEngine
from flask import Flask, request
from execjs import get
from werkzeug.exceptions import HTTPException
from server.exceptions import MissingParameterException, WrongFormatException

app = Flask(__name__)
node = get('Node')

node_env = node.compile('''
    const { JovoModelSnips } = require('jovo-model-snips');
    
    function convert(locale, model) {
      const snipsModelFiles = JovoModelSnips.fromJovoModel(model, locale);
      
      return snipsModelFiles[0].content;
    }
''')

@app.before_request
def check_request_type():
    ''' Checks if the current request MIME type is set to application/json '''
    if request.method == 'POST' and not request.is_json:
        raise WrongFormatException('Request body must be JSON.')

@app.route('/engine/train', methods=['POST'])
async def create_snips_engine():
    ''' Creates, trains and persists a Snips NLU Engine '''
    engine: SnipsNLUEngine = SnipsNLUEngine()
    locale: str = get_query_parameter('locale')
    bot_id: str = get_query_parameter('bot_id')

    snipsModel = node_env.call('convert', locale, request.json)
    engine.fit(snipsModel)

    # Create .engine/ if it doesn't exist
    engine_directory: str = '.engine'
    if not path.exists(engine_directory):
        makedirs(engine_directory)

    engine_path: str = path.join(engine_directory, bot_id)
    # If the engine path already exists, delete it first
    if path.exists(engine_path):
        shutil.rmtree(engine_path)

    engine.persist(engine_path)
    return '', 201

@app.route('/engine/parse', methods=['POST'])
async def parse_message():
    ''' Loads a Snips NLU Engine and parses a message through it '''
    bot_id: str = get_query_parameter('bot_id')

    engine_path: str = path.join('.engine', bot_id)
    engine: SnipsNLUEngine = SnipsNLUEngine.from_path(engine_path)
    request_json: Any = request.get_json()

    result = engine.parse(request_json['text'])
    return result, 200

@app.errorhandler(HTTPException)
def handle_exception(exception):
    response = exception.get_response()
    response.data = json.dumps({
        'code': exception.code,
        'description': exception.description,
        'name': type(exception).__name__,
    })
    response.content_type = 'application/json'
    return response, exception.code


def get_query_parameter(key: str) -> str:
    ''' Checks if a request query parameter is provided and returns it '''
    parameter = request.args.get(key)
    if not parameter:
        raise MissingParameterException('Missing parameter key: {key}'.format(key=key))

    return parameter
