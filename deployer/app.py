from flask import Flask, request
from flask import jsonify
from celery import Celery
from io import BytesIO
import tarfile
import time
import json
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
    if data['conf']['id'] is not None:
        sim_id = int(data['conf']['id'])
        print_flask('Using id given by server')
    else:
        #TODO:remove this, ID always comes from server
        id_gen = uuid.uuid4()
        sim_id = id_gen.int
    result = make_simualtion.delay(sim_id,data['model'],data['conf'])
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

def get_tarstream(file_data,file_name):
    pw_tarstream = BytesIO()

    pw_tar = tarfile.TarFile(fileobj=pw_tarstream, mode='w')

    tarinfo = tarfile.TarInfo(name=file_name)
    tarinfo.size = len(file_data)
    tarinfo.mtime = time.time()
    #tarinfo.mode = 0600

    pw_tar.addfile(tarinfo, BytesIO(file_data))
    pw_tar.close()

    pw_tarstream.seek(0)
    return pw_tarstream

@celery.task()
def make_simualtion(sim_id,model_data,conf_data):
    print_flask('Making new sim of id:'+str(sim_id))
    #Path where to put all data simlation needs
    #TODO:Replace this with /files after updating image in docker hub
    dest_path = '.'
    #For all files needed tar them and put them in container
    tar_model = get_tarstream(json.dumps(model_data).encode('utf8'),"model.json")
    tar_conf = get_tarstream(json.dumps(conf_data).encode('utf8'),"conf.json")
    print_flask('Conversion to tar for both jsons')

    container_made = client.containers.create("dioben/nntrackerua-simulation",name=str(sim_id),detach=True)
    print_flask('Containner with id:'+container_made.id + " was made")

    if conf_data['dataset_url'] is True:
        #TODO:Replace this section, container is stoped at the moment
        #Not sure where to put this, maybe in dockerfile
        print_flask("Preparing to download dataset...")
        helper_script = "curl smt.com"
        container_made.exec_run(helper_script)
    else:
        #Copy dataset files from path given to containner
        path_test = conf_data["dataset_test"]
        file_test = open(path_test,'rb').read()
        tar_test = get_tarstream(file_test,"dataset_test.csv")
        success = container_made.put_archive(dest_path, tar_test)
        print_flask('Put test tar:'+str(success))

        path_train = conf_data["dataset_train"]
        file_train = open(path_train,'rb').read()
        tar_train = get_tarstream(file_train,"dataset_train.csv")
        success = container_made.put_archive(dest_path, tar_test)
        print_flask('Put train tar:'+str(success))

    success = container_made.put_archive(dest_path, tar_model)
    print_flask('Put model tar:'+str(success))
    success = container_made.put_archive(dest_path, tar_conf)
    print_flask('Put concif tar:'+str(success))

    container_made.start()
    print_flask('Started script')

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