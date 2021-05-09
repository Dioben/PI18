from flask import Flask, request
from celery import Celery
import psycopg2


conn = psycopg2.connect(
    host="localhost",
    database="nntracker",
    user="root",
    password="postgres")


app = Flask(__name__)

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.route('/update', methods=['POST'])
def update_simulation():
    simulation_data = request.get_json()
    process_data(simulation_data)
    result = update_data_sent.delay(simulation_data)
    result.wait()
    return 'All good'

@app.route('/finish', methods=['POST'])
def finish_simulation():
    simulation_data = request.get_json()

    result = finish_data_sent.delay(simulation_data)
    result.wait()
    return 'All good'

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)

    return celery

app.config.update(
    broker_url = 'redis://localhost:6379',
    result_backend = 'redis://localhost:6379',

    task_serializer = 'json',
    result_serializer = 'json',
    accept_content = ['json'],
    timezone = 'Europe/Lisbon',
    enable_utc = True,
)
celery = make_celery(app)

@celery.task()
def update_data_sent(json_file):
    logger.info('hello')
    logger.info(len(json_file))
    logger.info(json_file.keys())
    process_data(json_file)
    return None

def process_data(data_dict):
    #print(data_dict['weights'])
    for i in range(len(data_dict['weights'])):
        layer_data = data_dict['weights'][i]
        print('layer ',i,':',len(layer_data))
    weights = {str(i) : data_dict['weights'][i][0] if data_dict['weights'][i] != [] else [] for i in range(len(data_dict['weights'])) }
    loss = data_dict['logs']['loss']
    accuracy = data_dict['logs']['accuracy']
    print(loss)
    print(accuracy)
    #print(weights)
    print(len(weights))
    return None


@celery.task()
def finish_data_sent(json):
    #Placeholder
    return None