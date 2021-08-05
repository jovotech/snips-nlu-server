import json
import shutil
from os import path
from flask.helpers import make_response
from snips_nlu import SnipsNLUEngine
from flask import Flask, request
from execjs import get

app = Flask(__name__)
node = get('Node')

node_env = node.compile('''
    const { JovoModelSnips } = require('jovo-model-snips');
    
    function convert(locale, model) {
      const snipsModelFiles = JovoModelSnips.fromJovoModel(model, locale);
      
      return snipsModelFiles[0].content;
    }
''')

def convertModel(locale, model):
    return node_env.call('convert', locale, model)

@app.route('/train', methods=['POST'])
async def create_snips_engine():
    engine = SnipsNLUEngine()
    locale = request.args.get('locale')
    if locale is None:
        # TODO Throw an error
        return 'not ok'
    snipsModel = convertModel(locale, request.json)

    engine.fit(snipsModel)
    bot_id = request.args.get('bot_id')
    if bot_id is None:
        # TODO Throw an error
        return 'not ok'

    engine_path: str = path.join('engine', bot_id)
    if path.exists(engine_path):
        shutil.rmtree(engine_path)

    engine.persist(engine_path)
    return 'ok'

@app.route('/parse', methods=['POST'])
async def parse_message():
    check_request_type()
    bot_id = request.args.get('bot_id')
    if bot_id is None:
        # TODO Throw an error
        return 'not ok'

    engine_path: str = path.join('engine', bot_id)
    engine = SnipsNLUEngine.from_path(engine_path)
    request_json = request.get_json()

    if not request_json:
        print('HERE')


    result = engine.parse(request.json['message'])
    return result

def check_request_type():
    if not request.is_json:
        raise WrongFormatException('Request body must be JSON.')

@app.errorhandler(Exception)
def handle_wrong_format(exception):
    response = make_response()
    response.data = json.dumps({
        'code': 422,
        'name': type(exception).__name__,
        'description': str(exception)
    })
    response.content_type = 'application/json'
    return response

