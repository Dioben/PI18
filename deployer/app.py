from flask import Flask, request
from flask import jsonify
from celery import Celery
import sys
import docker
import uuid

app = Flask(__name__)
client = docker.from_env()

@app.route('/simulations', methods=['POST'])
def make_simulation():
    print_flask('here')
    print_flask(request.data)
    data = request.get_json(force=True)
    print_flask('data'+str(len(data)))
    #Replace this for simulation id given to us
    id_gen = uuid.uuid4()
    sim_id = id_gen.int
    result = make_simualtion.delay(sim_id)
    result.wait()
    resp = jsonify(success=True)
    return resp

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

def print_flask(input):
    print(input, file=sys.stderr)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)

    return celery

app.config.update(
    broker_url = 'redis://celery_deployer:6380',
    result_backend = 'redis://celery_deployer:6380',

    task_serializer = 'json',
    result_serializer = 'json',
    accept_content = ['json'],
    timezone = 'Europe/Lisbon',
    enable_utc = True,
)
celery = make_celery(app)

@celery.task()
def make_simualtion(sim_id):
    print_flask('Making new sim of id:'+str(sim_id))
    container_made = client.containers.run("dioben/nntrackerua-simulation",name=str(sim_id),detach=True)
    print_flask('Containner with id:'+container_made.id + " was made")
    return None

@celery.task()
def delete_simulation(simulation_id):
    try:
        containner_kill = client.containers.get(simulation_id)
        containner_kill.kill()
    except Exception as e:
        print_flask('ERROR:'+str(e))
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
            print_flask('ERROR:','Given invalid command ',command)
    except Exception as e:
        print_flask('ERROR:'+str(e))
    return None