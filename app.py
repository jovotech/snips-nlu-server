from datetime import datetime
import io
import json
from os import path
from pathlib import Path
from typing import Union, Any
from snips_nlu import SnipsNLUEngine
import shutil
from flask import Flask, request
from execjs import get


app = Flask(__name__)
node = get('Node')

node_env = node.compile('''
    const { JovoModelRasa } = require('jovo-model-rasa');
    
    function convert(model) {
      const rasaModelFiles = JovoModelRasa.fromJovoModel(model);
      
      return rasaModelFiles[0].content;
    }
''')

def convertModel(model: Any) -> Any:
    return node_env.call('convert', model)

@app.route('/train', methods=['POST'])
async def create_snips_engine():
    engine = SnipsNLUEngine()
    with io.open('dataset.json') as dataset_file:
        dataset = json.load(dataset_file)
    engine.fit(dataset)
    bot_id: Union[str, None] = request.args.get('bot_id')
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
    bot_id: Union[str, None] = request.args.get('bot_id')
    if bot_id is None:
        # TODO Throw an error
        return 'not ok'

    engine_path: str = path.join('engine', bot_id)
    engine = SnipsNLUEngine.from_path(engine_path)
    result = engine.parse(request.json['message'])
    return result

