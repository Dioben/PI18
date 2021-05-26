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
import tensorflow as tf
import numpy as np
import re
import os
import pickle
from sklearn.model_selection import KFold

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

#Convert from numpy type supported to pickle
def numpy_to_pickle(file_data_features,file_data_labels,conf_json,type_file='train'):
    print('convert data to pickle:',type_file)
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
        # path = f'./{type_file}'
        # np.savez_compressed(path, simulation_feature_name=file_data_features, simulation_label_name=file_data_labels)
        # file_object = open(path+'.npz','rb')
        # file_data = file_object.read()
        # file_object.close()
        file_dic = {'simulation_feature_name' : file_data_features, 'simulation_label_name' : file_data_labels}
        file_data = pickle.dumps(file_dic)
        print('after pickle')
    except Exception as e:
        print('ERROR:'+str(e))
        return None
    return file_data

#From any file object to Dataset and from there to numpy
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
                print_flask('Type stuff first ds:')
                print_flask(type(features))
                print_flask(type(labels))
                dataset = tf.data.Dataset.from_tensor_slices((features, labels))
        else:
            #Non suported file extension
            dataset = None
            return None

        dataset_numpy_features = np.array([x for x,y in dataset.as_numpy_iterator()])
        dataset_numpy_label = np.array([y for x,y in dataset.as_numpy_iterator()])

        #For testing purposes
        # print_flask(len(dataset_numpy_features))
        # print_flask(len(dataset_numpy_label))
        
        # dnf = tf.convert_to_tensor(dataset_numpy_features)
        # dnl = tf.convert_to_tensor(dataset_numpy_label)

        # print_flask('Type stuff:')
        # print_flask(type(dataset_numpy_features))
        # print_flask(type(dataset_numpy_features[0]))

        # print_flask('New dataset test')
        # dataset = tf.data.Dataset.from_tensor_slices((dnf, dnl))
        # print_flask('After new ds')

        return dataset_numpy_features,dataset_numpy_label
    except Exception as e:
        print_flask('Error:')
        print_flask(e)
        pass
    return None


def download_dataset(url,filename):
    local_filename = "./dataset/" + filename
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("done ", local_filename)
    return local_filename


#Done in order to have a second task to handle k-fold simulations parrallely
#Only thing it does is convert to numpy and continue with start_simualtion 
@celery.task()
def make_k_fold_simulation(sim_id,model_data,conf_data,train_data_X,train_data_y,test_data_X,test_data_y,val_data_X,val_data_y):
    print_flask('K-fold simulation'+str(sim_id))
    train_data_X = np.array(train_data_X)
    train_data_y = np.array(train_data_y)
    test_data_X = np.array(test_data_X)
    test_data_y = np.array(test_data_y)
    val_data_X = np.array(val_data_X)
    val_data_y = np.array(val_data_y)
    start_simulation(sim_id,model_data,conf_data,train_data_X,train_data_y,test_data_X,test_data_y,val_data_X,val_data_y)

@celery.task()
def make_simualtion(sim_id,model_data,conf_data):
    print_flask('Making new sim of id:'+str(sim_id))
    #Check config for k-fold validation, get data -> numpy and then use stratifield k-fold
    #Get data -> numpy
    if conf_data["dataset_url"]:
        #download
        path_train = download_dataset(conf_data["dataset_train"], "dataset_train")
        path_test = download_dataset(conf_data["dataset_test"], "dataset_test")
        path_val = download_dataset(conf_data["dataset_val"], "dataset_val")
    else:
        path_test = conf_data["dataset_test"]
        path_train = conf_data["dataset_train"]
        path_val = conf_data["dataset_val"]

    #Attention, should not be used in k-fold
    dataset_test_x,dataset_test_y = parse_to_numpy(path_test,conf_data,'test')

    dataset_train_x,dataset_train_y = parse_to_numpy(path_train,conf_data,'train')

    dataset_val_x,dataset_val_y = parse_to_numpy(path_val,conf_data,'validation')

    #K-fold or not
    k_fold_number = int(conf_data['k-fold_validation'])
    if k_fold_number > 1:
        #TODO:Rework to make everying list here,mght give problems
        #dataset_train_val = np.append(dataset_train,dataset_val)
        #print_flask(dataset_train_val[0])
        dataset_train_val_features = np.append(dataset_train_x,dataset_val_x)
        dataset_train_val_labels = np.append(dataset_train_y,dataset_val_y)
        print_flask('Dump of shapes after append')
        print_flask(dataset_train_val_features.shape)
        print_flask(dataset_train_val_labels.shape)
        x_test = list(x_test)
        y_test = list(y_test)
        kfold = KFold(n_splits=k_fold_number, shuffle=True, random_state=1048596)
        for train_index, val_index in kfold.split(dataset_train_val_features):
            #Stratified fold for train and validation
            x_train_kf, x_val_kf = list(dataset_train_val_features[train_index]), list(dataset_train_val_features[val_index])
            y_train_kf, y_val_kf = list(dataset_train_val_labels[train_index]), list(dataset_train_val_labels[val_index])

            make_k_fold_simulation.delay(sim_id,model_data,conf_data,x_train_kf,y_train_kf,x_test,y_test,x_val_kf,y_val_kf)
            #TODO:Replace this
            sim_id+=1
    else:
        start_simulation(sim_id,model_data,conf_data,dataset_train_x,dataset_train_y,dataset_test_x,dataset_test_y,dataset_val_x,dataset_val_y)
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

    #Copy dataset files from path given to containner
    #After read convert to "normalized" file format to .npz
    print(conf_data)
    file_test = numpy_to_pickle(test_data_X,test_data_y,conf_data,'test')
    tar_test = get_tarstream(file_test,"dataset_test.npz")
    success = container_made.put_archive(dest_path, tar_test)
    print_flask('Put test tar:'+str(success))

    file_train = numpy_to_pickle(train_data_X,train_data_y,conf_data,'train')
    tar_train = get_tarstream(file_train,"dataset_train.npz")
    success = container_made.put_archive(dest_path, tar_train)
    print_flask('Put train tar:'+str(success))

    file_val = numpy_to_pickle(val_data_X,val_data_y,conf_data,'validation')
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