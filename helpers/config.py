import os
import json


is_prod = os.environ.get('IS_HEROKU', None)
config = {k: os.environ.get(k) for k in os.environ.keys()} if is_prod else json.load(open('config.json'))
