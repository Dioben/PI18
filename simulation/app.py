import tensorflow as tf
from tensorflow.keras.layers import LayerNormalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D, Input, BatchNormalization
import time
import numpy as np
import requests
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import model_from_json
import re
import os
import urllib.request
import json
import sys

print("Simulation start",file=sys.stderr)
#Read files from pre-defined directory
DIR_FILES = "."
with open(os.path.join(DIR_FILES,"model.json"),"r") as model_file:
    model_json = model_file.read()
with open(os.path.join(DIR_FILES,"conf.json"),"r") as conf_file:
    conf_txt = conf_file.read()
    conf_json = json.loads(conf_txt)


#Get configuration paramteres
BATCH_SIZE = int(conf_json['batch_size'])
EPOCHS = int(conf_json['epochs'])
EPOCH_PERIOD = int(conf_json['epoch_period'])
LEARNING_RATE = float(conf_json['learning_rate'])

#Search directory for files dataset_test dataset_train
print(os.listdir())
for file_name in os.listdir():
    if 'dataset_test' in file_name:
        test_path = file_name
    if 'dataset_train' in file_name:
        train_path = file_name
    if 'dataset_val' in file_name:
        val_path = file_name

print('test:',test_path)
print('train:',train_path)
print('val:',val_path)

def load_database(path_given,conf_json,type_file='train'):
    #File path given to file in VFS
    file_arr =  os.path.basename(path_given).split('.')
    file_name = file_arr[0]
    file_extension = file_arr[1]

    if 'csv' in file_arr[1]:
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
    return dataset

dataset_train = load_database(train_path,conf_json)
dataset_test = load_database(test_path,conf_json,type_file="test")
dataset_val = load_database(val_path,conf_json,type_file="validation")
print(type(dataset_test),file=sys.stderr)
print(type(dataset_train))
print(type(dataset_val))

#Get URL to aggregator
url = 'http://parser:6000/update'

def get_optimizer_tensorflow(conf_json,base_learning_rate):
    if 'adadelta' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Adadelta(lr=base_learning_rate)
    elif 'adagrad' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Adagrad(lr=base_learning_rate)
    elif 'adam' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Adam(lr=base_learning_rate)
    elif 'ftrl' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Ftrl(lr=base_learning_rate)
    elif 'nadam' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Nadam(lr=base_learning_rate)
    elif 'rmsprop' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.RMSprop(lr=base_learning_rate)
    elif 'sgd' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.SGD(lr=base_learning_rate)

def get_loss_func_tensorflow(conf_json):
    print(type(conf_json['from_logits']))
    identifier = {"class_name": conf_json['loss_function'],
              "config": {"from_logits": conf_json['from_logits']} }
    loss = tf.keras.losses.get(identifier)
    return loss

optimizer_choosen = get_optimizer_tensorflow(conf_json,LEARNING_RATE)
loss_function_choosen = get_loss_func_tensorflow(conf_json)


#Get Model
model = model_from_json(model_json)
model.compile(optimizer=optimizer_choosen,
              loss=loss_function_choosen,
              metrics=['accuracy'])
json_model = model_json

#Used because keras seems to use both lists and numpy arrays in toweights
def listify_numpy_arr(lst):
    if not isinstance(lst,list) and 'numpy.ndarray' not in str(type(lst)):
        return lst
    for i in range(len(lst)):
        if 'numpy.ndarray' in str(type(lst[i])):
            lst[i] = listify_numpy_arr(lst[i].tolist())
        else:
            lst[i] = listify_numpy_arr(lst[i])
    return lst

class DataAggregateCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        if epoch % EPOCH_PERIOD == 0 or epoch == EPOCHS-1:
            print('Post to aggregator',file=sys.stderr)

            logs = {i : logs[i] for i in logs.keys()}

            print(f"Logs for epoch {epoch} are: {logs}")

            weigths = []
            #get_weights already gives you two arrays, first is actual weights, the rest are bias(non-treinable weights)
            for i in range(len(model.layers)):
                if model.layers[i].weights != None:
                    out = listify_numpy_arr(model.layers[i].get_weights())
                    #print(f'For Layer {i} got weights {out}')
                    weigths.append(out)
            print('Here after wigths')
            #print(f'For Layer {i} got output {np.array(features[i]).shape}')

            #weigths = [model.layers[i].get_weigths() for i in range(len(model.layers)) if model.layers[i].weights != []] 

            #print(f"middle_layer_for_real:{middle_layers_outputs}")

            res_dic = {}
            
            res_dic["model"] = json_model

            res_dic["logs"] = logs

            res_dic["sim_id"] = conf_json["id"]

            res_dic["epoch"] = epoch

            res_dic["weights"] = weigths

            data = res_dic
            print('Here after json')
            print(len(data),file=sys.stderr)
            url = 'http://parser:6000/update'
            if epoch == EPOCHS-1:
                url = 'http://parser:6000/finish'
            try:
                headers = {'Content-type': 'application/json'}
                res = requests.post(url, json = data,headers=headers,timeout=50)
                print('Post status:',res,file=sys.stderr)
                if epoch == EPOCHS - 1:
                    url = 'http://deployer:7000/simulations/' + conf_json["id"]
                    res = requests.delete(url)
                    print('Delete status:', res, file=sys.stderr)
            except Exception as error:
                print(error)
                print("Exception")
            print('Here after post')

print('Learning rate:',LEARNING_RATE)
model.fit(dataset_train, batch_size=BATCH_SIZE, epochs=EPOCHS
          , callbacks= [DataAggregateCallback()], validation_data=dataset_val)
model.evaluate(dataset_test, batch_size=BATCH_SIZE, verbose=0)

