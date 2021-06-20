import requests
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
import re
import os
import pickle
import psutil

app = Flask(__name__)
client = docker.from_env()

#ENV variables
broker_url = 'redis://celery_deployer:6380' if "BROKER_URL" not in os.environ else os.environ['BROKER_URL']
result_backend = 'redis://celery_deployer:6380' if "RESULT_BACKEND" not in os.environ else os.environ['RESULT_BACKEND']
sim_image_name = 'dioben/nntrackerua-simulation' if "DEPLOYABLE_NAME" not in os.environ else os.environ['DEPLOYABLE_NAME']

parser_url = 'http://parser:6000' if "PARSER_URL" not in os.environ else os.environ['PARSER_URL']

docker_components = ['timescaledb','grafana','tracker-server','tracker-deployer',
        'tracker-deployer-worker','redis_deployer','tracker-parser','tracker-parser-worker','redis'] if "COMPONENTS" not in os.environ else os.environ['COMPONENTS'].split(',')

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
    resp = jsonify(success=True)
    return resp

@app.route('/simulations/<simulation_id>', methods=['DELETE'])
def delete_simulation(simulation_id):
    result = delete_simulation.delay(simulation_id)
    return 'All good'

@app.route('/simulations/<simulation_id>/<command>', methods=['POST'])
def change_simulation(simulation_id,command):
    result = change_simulation.delay(simulation_id,command)
    return 'All good'

@app.route('/simulations_statistics', methods=['GET'])
def simulation_stats():
    sys_info = get_system_info()
    docker_info = get_docker_container_info()
    info = {'system_information': sys_info, 'docker_containers_info' : docker_info}
    print_flask('Final')
    print_flask(str(info))
    resp = jsonify(info)
    return resp

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_system_info():
    svmem = psutil.virtual_memory()
    info = {}
    info['Total CPU Usage'] = psutil.cpu_percent()
    info['Total Memory Usage'] = svmem.percent

    print_flask("Total cores:" + str(psutil.cpu_count(logical=True)))
    print_flask("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print_flask(f"Core {i}: {percentage}%")
    print_flask(f"Total CPU Usage: {psutil.cpu_percent()}%")
    # get the memory details

    print_flask(f"Total: {get_size(svmem.total)}")
    print_flask(f"Available: {get_size(svmem.available)}")
    print_flask(f"Used: {get_size(svmem.used)}")
    print_flask(f"Percentage: {svmem.percent}%")
    print_flask("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for i in range(len(partitions)):
        partition = partitions[i]
        print_flask(f"=== Device: {partition.device} ===")
        print_flask(f"  Mountpoint: {partition.mountpoint}")
        print_flask(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print_flask(f"  Total Size: {get_size(partition_usage.total)}")
        print_flask(f"  Used: {get_size(partition_usage.used)}")
        print_flask(f"  Free: {get_size(partition_usage.free)}")
        print_flask(f"  Percentage: {partition_usage.percent}%")
        info[f'Disc{i} Percentage Usage'] = partition_usage.percent
    return info

def get_docker_container_info():
    print_flask('Docker stats')
    info = {}
    for containers in client.containers.list():
        if not containers.name in docker_components:
            stream1 = containers.stats(decode=None, stream = False)
            stream2 = containers.stats(decode=None, stream = False)
            print_flask(stream1)
            print_flask(stream2)
            info[containers.name] = parse_docker_stats(stream1,stream2)
    return info

def parse_docker_stats(info_dict,info_dict2):
    try:
        formated_info = {}

        svmem = psutil.virtual_memory()
        cpu_usage1 = info_dict['cpu_stats']['cpu_usage']['total_usage']
        sys_cpu_usage1 = info_dict['cpu_stats']['system_cpu_usage']
        cpu_count = info_dict['cpu_stats']['online_cpus']

        cpu_usage2 = info_dict2['cpu_stats']['cpu_usage']['total_usage']
        sys_cpu_usage2 = info_dict2['cpu_stats']['system_cpu_usage']

        cpuPercent = 0.0
        cpuDelta = cpu_usage2 - cpu_usage1
        systemDelta = sys_cpu_usage2 - sys_cpu_usage1
        print_flask(cpuDelta)
        print_flask(systemDelta)
        if systemDelta > 0.0 and cpuDelta > 0.0:
            cpuPercent = (cpuDelta / systemDelta) * cpu_count * 100
        print_flask(cpuPercent)

        memory_usage_bytes = info_dict['memory_stats']['usage']
        memory_max_bytes = info_dict['memory_stats']['max_usage']
        print_flask('memory bytes')
        print_flask(memory_usage_bytes)
        print_flask(memory_max_bytes)
        print_flask(svmem.total)
        memory_usage_percentage = memory_usage_bytes/memory_max_bytes

        cpuPercent = cpuPercent / cpu_count
        formated_info['CPU Percentage Usage'] = cpuPercent
        formated_info['Memory Percentage Usage'] = memory_usage_percentage
        return formated_info
    except Exception as e:
        print_flask('ERROR:'+str(e))
    return {}
    
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
    broker_url = broker_url,
    result_backend = result_backend,

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

def read_file(path):
    print('reading data from file:',path)
    file_obj = open(path,'rb')
    file_data = file_obj.read()
    file_obj.close()
    return file_data



def download_dataset(url,filename,simid):
    local_filename = "../all_datasets/"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        fname = re.findall('filename=(.+)', r.headers.get('content-disposition'))
        local_filename = local_filename + str(simid) + "-" + filename + "." + fname[0].split('"')[1].split(".")[-1]
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("done ", local_filename)
    return local_filename



@celery.task()
def make_simualtion(sim_id,model_data,conf_data):
    print_flask('Making new sim of id:'+str(sim_id))
    #Check config for k-fold validation, get data -> numpy and then use stratifield k-fold
    #Get data -> numpy
    if conf_data["dataset_url"]:
        #download
        path_train = download_dataset(conf_data["dataset_train"], "dataset_train", conf_data["id"])
        path_test = download_dataset(conf_data["dataset_test"], "dataset_test", conf_data["id"])
        path_val = download_dataset(conf_data["dataset_val"], "dataset_val", conf_data["id"])
    else:
        path_test = conf_data["dataset_test"]
        path_train = conf_data["dataset_train"]
        path_val = conf_data["dataset_val"]

    #K-fold or not
    k_fold_number = int(conf_data['k-fold_validation'])
    if k_fold_number > 1:
        print_flask('K-fold for '+str(k_fold_number))
        #For each fold that will be made make a new simulation with an index provided to simulation
        sim_idx_lst = conf_data['k-fold_ids']
        for i in range(k_fold_number):
            start_simulation(sim_idx_lst[i],model_data,conf_data,path_train,path_val,path_test,i)
    else:
        start_simulation(sim_id,model_data,conf_data,path_train,path_val,path_test)
    
    cleanup_data(path_train,path_val,path_test)
    return None

def cleanup_data(path_train,path_val,path_test):
    print_flask('Cleanup after sim creation')
    if os.path.exists(path_train):
        os.remove(path_train)
    if os.path.exists(path_val):
        os.remove(path_val)
    if os.path.exists(path_test):
        os.remove(path_test)

def get_extension(path_given):
    file_arr =  os.path.basename(path_given).split('.')
    file_name = file_arr[0]
    file_extension = file_arr[1]
    return file_extension

def start_simulation(sim_id,model_data,conf_data,path_train,path_val,path_test,k_fold_idx = None):
    if k_fold_idx != None:
        print_flask(str(conf_data))
        print_flask('K fold index:'+str(k_fold_idx))
        conf_data['k-fold_index'] = k_fold_idx
    #For all files needed tar them and put them in container
    dest_path = '/app'
    tar_model = get_tarstream(json.dumps(model_data).encode('utf8'),"model.json")
    print_flask(str(tar_model))
    tar_conf = get_tarstream(json.dumps(conf_data).encode('utf8'),"conf.json")
    print_flask('Conversion to tar for both jsons')

    env_dict = {'PARSER_URL' : parser_url}
    container_made = client.containers.create(sim_image_name,name=str(sim_id),detach=True,environment=env_dict)
    print_flask('Containner with id:'+container_made.id + " was made")

    #Copy dataset files from path given to containner
    print(conf_data)
    file_test = read_file(path_test)
    test_extension = get_extension(path_test)
    print_flask(test_extension)
    tar_test = get_tarstream(file_test,"dataset_test."+test_extension)
    success = container_made.put_archive(dest_path, tar_test)
    print_flask('Put test tar:'+str(success))

    file_train = read_file(path_train)
    train_extension = get_extension(path_train)
    tar_train = get_tarstream(file_train,"dataset_train."+train_extension)
    success = container_made.put_archive(dest_path, tar_train)
    print_flask('Put train tar:'+str(success))

    file_val = read_file(path_val)
    val_extension = get_extension(path_val)
    tar_val = get_tarstream(file_val,"dataset_val."+val_extension)
    success = container_made.put_archive(dest_path, tar_val)
    print_flask('Put val tar:'+str(success))

    success = container_made.put_archive(dest_path, tar_model)
    print_flask('Put model tar:'+str(success))
    success = container_made.put_archive(dest_path, tar_conf)
    print_flask('Put config tar:'+str(success))

    networks_available = client.networks.list(names=['pi18_default'])
    network = networks_available[0]
    network.connect(container_made)
    container_made.start()
    print_flask('Started script')


@celery.task()
def delete_simulation(simulation_id):
    try:
        containner_kill = client.containers.get(simulation_id)
        containner_kill.remove(force=True)
    except Exception as e:
        print_flask('ERROR:'+str(e))
    return None

@celery.task()
def change_simulation(simulation_id,command):
    try:
        containner = client.containers.get(simulation_id)
        if 'START' in command:
            if containner.status == 'paused':
                containner.unpause()
            else:
                print_flask('ERROR:Trying to unpause while running')
        elif 'PAUSE' in command:
            if containner.status == 'running':
                containner.pause()
            else:
                print_flask('ERROR:Trying to pause while paused already')
        elif 'STOP' in command:
            if containner.status == 'running':
                containner.stop()
            else:
                print_flask('ERROR:Trying to stop while not running')
        else:
            print_flask('ERROR:','Given invalid command ',command)
    except Exception as e:
        print_flask('ERROR:'+str(e))
    return None