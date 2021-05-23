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
import tensorflow as tf
import numpy as np
import re
import os
import pickle
from sklearn.model_selection import StratifiedKFold

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


def convert_data(file_data_features,file_data_labels,conf_json,type_file='train'):
    print('convert data to pickle:',type_file)
    #Converts from this file object to standard .npz
    try:
        #Pickle numpy files
        if type_file == "train":
            simulation_feature_name = "x_train"
            simulation_label_name = "y_train"
        elif type_file == 'test':
            simulation_feature_name = "x_test"
            simulation_label_name = "y_test"
        elif type_file == 'validation':
            simulation_feature_name = "x_val"
            simulation_label_name = "y_val"
        
        print('before pickle')
        file_dic = {simulation_feature_name : file_data_features, simulation_label_name : file_data_labels}
        file_data = pickle.dumps(file_dic)
        print('after pickle')
    except Exception as e:
        print('ERROR:'+str(e))
        return None
    return file_data

def parse_to_numpy(path_given,conf_json,type_file='train'):
    print('convert data for',path_given)
    #Converts from this file object to numpy
    try:
        #File path given to file in conf
        file_arr =  os.path.basename(path_given).split('.')
        file_name = file_arr[0]
        file_extension = file_arr[1]

        BATCH_SIZE = conf_json['batch_size']
        if 'csv' in file_arr[1]:
            print('File is csv')
            #If it's a csv it's expect of conf to have this extra
            LABEL_COLUMN = conf_json['label_collumn']
            dataset = tf.data.experimental.make_csv_dataset(
                path_given,
                batch_size=BATCH_SIZE,
                label_name=LABEL_COLUMN,
                num_epochs=1,
                ignore_errors=True)
        elif 'npz' in file_arr[1]:
            print('File is npz')
            with np.load(path_given) as numpy_data:
                if type_file == "train":
                    feature_name = conf_json['train_feature_name']
                    label_name = conf_json['train_label_name']
                elif type_file == 'test':
                    feature_name = conf_json['test_feature_name']
                    label_name = conf_json['test_label_name']
                elif type_file == 'validation':
                    feature_name = conf_json['val_feature_name']
                    label_name = conf_json['val_label_name']
                print(type_file)
                features = numpy_data[feature_name]
                labels = numpy_data[label_name]
                dataset = tf.data.Dataset.from_tensor_slices((features, labels))
                dataset = dataset.shuffle(len(labels)).batch(BATCH_SIZE)
        else:
            #Non suported file extension
            dataset = None
            return None
        
        list_dataset = list(dataset.as_numpy_iterator())
        return list_dataset
    return None


@celery.task()
def make_simualtion(sim_id,model_data,conf_data):
    print_flask('Making new sim of id:'+str(sim_id))
    #Check config for k-fold validation, get data -> numpy and then use stratifield k-fold
    #Get data -> numpy
    
    #Attention, should not be used in k-fold
    path_test = conf_data["dataset_test"]
    dataset_test = parse_to_numpy(path_test,conf_data,'test')

    path_train = conf_data["dataset_train"]
    dataset_train = parse_to_numpy(path_train,conf_data,'train')

    path_val = conf_data["dataset_val"]
    dataset_val = parse_to_numpy(path_val,conf_data,'validation')

    x_test = [x for x,y in dataset_test]
    y_test = [y for x,y in dataset_test]
    #K-fold or not
    k_fold_number = int(conf_data['k-fold_validation'])
    if k_fold_number > 1:
        dataset_train_val = np.append(dataset_train,dataset_val)
        dataset_train_val_features = [x for x,y in dataset_train_val]
        dataset_train_val_labels = [y for x,y in dataset_train_val]
        kfold = StratifiedKFold(n_splits=k_fold_number, shuffle=True, random_state=1048596)
        for train_index, val_index in kfold.split(dataset_train_val_features, dataset_train_val_labels):
            #Stratified fold for train and validation
            x_train_kf, x_val_kf = dataset_train_val_features[train_index], dataset_train_val_features[val_index]
            y_train_kf, y_val_kf = dataset_train_val_labels[train_index], dataset_train_val_labels[val_index]
            start_simulation(sim_id,model_data,conf_data,x_train_kf,y_train_kf,x_test,y_test,x_val_kf,y_val_kf)
            #TODO:Replace this
            sim_id+=1
    else:
        #Do just once a simulation
        x_train = [x for x,y in dataset_train]
        y_train = [y for x,y in dataset_train]

        x_val = [x for x,y in dataset_val]
        y_val = [y for x,y in dataset_val]
        start_simulation(sim_id,model_data,conf_data,x_train,y_train,x_test,y_test,x_val,y_val)
    return None


def start_simulation(sim_id,model_data,conf_data,train_data_X,train_data_y,test_data_X,test_data_y,val_data_X,val_data_y):
    #For all files needed tar them and put them in container
    dest_path = '/app'
    tar_model = get_tarstream(json.dumps(model_data).encode('utf8'),"model.json")
    print_flask(str(tar_model))
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
        #After read convert to "normalized" file format to .npz
        print(conf_data)
        file_test = convert_data(test_data_X,test_data_y,conf_data,'test')
        tar_test = get_tarstream(file_test,"dataset_test.npz")
        success = container_made.put_archive(dest_path, tar_test)
        print_flask('Put test tar:'+str(success))

        file_train = convert_data(train_data_X,train_data_y,conf_data,'train')
        tar_train = get_tarstream(file_train,"dataset_train.npz")
        success = container_made.put_archive(dest_path, tar_train)
        print_flask('Put train tar:'+str(success))

        file_val = convert_data(val_data_X,val_data_y,conf_data,'validation')
        tar_train = get_tarstream(file_val,"dataset_val.npz")
        success = container_made.put_archive(dest_path, tar_train)
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