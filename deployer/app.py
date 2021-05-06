from flask import Flask, request
from celery import Celery

app = Flask(__name__)

@app.route('/simulations', methods=['POST'])
def make_simulation():
    data = request.get_json()

    result = make_simualtion.delay(model_data,dataset_data,conf_data)
    result.wait() 
    #Should return the simulation ID
    return 'All good'

@app.route('/simulations/<simulation_id>', methods=['DELETE'])
def delete_simulation(simulation_id):
    result = delete_simulation.delay(simulation_id)
    result.wait() 
    return 'All good'

@app.route('/simulations/<simulation_id>/<command>', methods=['POST'])
def change_simulation(simulation_id,command):
    result = change_simulation.delay(simulation_id,command)
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
def make_simualtion(model_data,dataset_data,conf_data):
    #Placeholder
    return None

@celery.task()
def delete_simulation(simulation_id):
    #Placeholder
    return None

@celery.task()
def change_simulation(simulation_id,command):
    #Placeholder
    return None