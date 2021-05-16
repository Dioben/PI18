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


#Search directory for files dataset_test dataset_train
print(os.listdir())
for file_name in os.listdir():
    if 'dataset_test' in file_name:
        test_path = file_name
    if 'dataset_train' in file_name:
        train_path = file_name

print('test:',test_path)
print('train:',train_path)

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
            features = numpy_data[feature_name]
            labels = numpy_data[label_name]
            dataset = tf.data.Dataset.from_tensor_slices((features, labels))
            dataset = dataset.shuffle(len(labels)).batch(BATCH_SIZE)
    else:
        #Non suported file extension
        dataset = None
    return dataset

dataset_train = load_database(train_path,conf_json)
dataset_test = load_database(test_path,conf_json)
print(type(dataset_test),file=sys.stderr)
print(type(dataset_train))

#Get URL to aggregator
url = 'http://parser:6000'

def get_optimizer_tensorflow(conf_json):
    if 'adadelta' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Adadelta()
    elif 'adagrad' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Adagrad()
    elif 'adam' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Adam()
    elif 'ftrl' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Ftrl()
    elif 'nadam' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.Nadam()
    elif 'rmsprop' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.RMSprop()
    elif 'sgd' in conf_json['optimizer'].lower():
        return tf.keras.optimizers.SGD()

def get_loss_func_tensorflow(conf_json):
    print(type(conf_json['from_logits']))
    identifier = {"class_name": conf_json['loss_function'],
              "config": {"from_logits": conf_json['from_logits']} }
    loss = tf.keras.losses.get(identifier)
    return loss

optimizer_choosen = get_optimizer_tensorflow(conf_json)
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
        if epoch % EPOCH_PERIOD == 0:
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

            #print(f'For Layer {i} got output {np.array(features[i]).shape}')

            #weigths = [model.layers[i].get_weigths() for i in range(len(model.layers)) if model.layers[i].weights != []] 

            #print(f"middle_layer_for_real:{middle_layers_outputs}")

            res_dic = {}
            
            res_dic["model"] = json_model

            res_dic["logs"] = logs

            res_dic["sim_id"] = conf_json["id"]

            res_dic["epoch"] = epoch

            res_dic["weights"] = weigths

            data = json.dumps(res_dic)
            print(len(data),file=sys.stderr)
            res = requests.post(url, json = data)
            print('Post status:',res,file=sys.stderr)

model.fit(dataset_train, batch_size=BATCH_SIZE, epochs=EPOCHS
          , callbacks= [DataAggregateCallback()])
model.evaluate(dataset_test, batch_size=BATCH_SIZE, verbose=0)

