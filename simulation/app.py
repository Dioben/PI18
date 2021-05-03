import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D, Input, BatchNormalization
import time
import numpy as np
import requests
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.utils import to_categorical
import re
import os
import urllib.request


#Get configuration paramteres
BATCH_SIZE = ???
EPOCHS = ???
EPOCH_PERIOD = ???
LABEL_COLUMN = ???

#Get URL to aggregator
url = '/localhost/aggregator'

#Get Model Json
json_config = []
#Get path to dataset file
path_given = ''
#Get Model
model = keras.models.model_from_json(json_config)
json_model = model.to_json()


def load_database(path_given):
    #File path given to file in VFS
    file_arr =  os.path.basename(path_given).split('.')
    file_name = file_arr[0]
    file_extension = file_arr[1]

    if 'csv' in file_arr[1]:
      dataset = tf.data.experimental.make_csv_dataset(
          path_given,
          batch_size=BATCH_SIZE,
          label_name=LABEL_COLUMN,
          na_value="?",
          num_epochs=1,
          ignore_errors=True)
    elif 'npy' in file_arr[1]:
        with np.load(path_given) as numpy_data:
            features = numpy_data["features"]
            labels = numpy_data["labels"]
            dataset = tf.data.Dataset.from_tensor_slices((features, labels))
            dataset = dataset.shuffle(len(labels)).batch(BATCH_SIZE)
    else:
        #Non suported file extension
        dataset = None
    return dataset


dataset = load_database(path_given)

class DataAggregateCallback(keras.callbacks.Callback):
        if epoch % EPOCH_PERIOD == 0:

            print('Post to aggregator')

            logs = {i : logs[i] for i in logs.keys()}

            print(f"Logs for epoch {epoch} are: {logs}")

            feature_extractor = keras.Model(inputs=model.inputs,
                                    outputs=[layer.output for layer in model.layers])
            feature_extractor.compile()
            features = feature_extractor(x_train)
            print(f"features:{features}")

            middle_layers_outputs = [layer_out.numpy()  for layer_out in features]

            weigths = []
            #get_weights already gives you two arrays, first is actual weights, the rest are bias(non-treinable weights)
            for i in range(len(model.layers)):
            if model.layers[i].weights != None:
                out = model.layers[i].get_weights()
                #print(f'For Layer {i} got weights {out}')
                weigths.append(out)

            #print(f'For Layer {i} got output {np.array(features[i]).shape}')

            #weigths = [model.layers[i].get_weigths() for i in range(len(model.layers)) if model.layers[i].weights != []] 

            #print(f"middle_layer_for_real:{middle_layers_outputs}")

            res_dic = {}
            
            res_dic["model"] = json_model

            res_dic["middle_layers"] = middle_layers_outputs

            res_dic["logs"] = logs

            res_dic["weights"] = weigths

            data = pickle.dumps(res_dic)
            res = requests.post(url, data = data)
            print('Post status:',res)



model.fit(dataset, batch_size=BATCH_SIZE, epochs=EPOCHS
          , callbacks= [DataAggregateCallback()], validation_data=(x_val, y_val),)
model.evaluate(x_test, y_test, batch_size=128, verbose=0)

