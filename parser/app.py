from flask import Flask, request
from celery import Celery

app = Flask(__name__)

@app.route('/update', methods=['POST'])
def update_simulation():
    #simulation_data = request.get_json()

    result = update_data_sent.delay(simulation_data)
    result.wait() 
    return 'All good'

@app.route('/finish', methods=['POST'])
def finish_simulation():
    #simulation_data = request.get_json()

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
def update_data_sent(json):
    #Placeholder
    return None

@celery.task()
def finish_data_sent(json):
    #Placeholder
    return None