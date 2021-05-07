from flask import Flask, request
from celery import Celery
import docker
import uuid

app = Flask(__name__)
client = docker.from_env()

@app.route('/simulations', methods=['POST'])
def make_simulation():
    try:
        data = request.get_json()
        print('data')
        id_gen = uuid.uuid4()
        sim_id = id_gen.int
        result = make_simualtion.delay(sim_id)
        result.wait()
        #Should return the simulation ID
        return sim_id
    except Exception as e:
        print('ERROR:',e)
    return None

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
    broker_url = 'redis://localhost:6380',
    result_backend = 'redis://localhost:6380',

    task_serializer = 'json',
    result_serializer = 'json',
    accept_content = ['json'],
    timezone = 'Europe/Lisbon',
    enable_utc = True,
)
celery = make_celery(app)

@celery.task()
def make_simualtion(sim_id):
    try:
        container_made = client.containers.run("dioben/nntrackerua-simulation",name=str(sim_id),detach=True)
        print('Containner with id:'+container_made.id + " was made")
    except Exception as e:
        print('ERROR:',e)
    return None

@celery.task()
def delete_simulation(simulation_id):
    try:
        containner_kill = client.containers.get(simulation_id)
        containner_kill.kill()
    except Exception as e:
        print('ERROR:',e)
    return None

@celery.task()
def change_simulation(simulation_id,command):
    try:
        containner = client.containers.get(simulation_id)
        if 'START' in command:
            containner.unpause()
        elif 'PAUSE' in command:
            containner.pause()
        elif 'STOP' in command:
            containner.stop()
        else:
            print('ERROR:','Given invalid command ',command)
    except Exception as e:
        print('ERROR:',e)
    return None