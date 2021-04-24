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
            data = {}

            keys = list(logs.keys())
            logs = {key : logs[i] for key in logs.keys()}

            print(f"Logs for epoch {epoch} are: {logs}")


            #Model made to extract middle layer outputs
            feature_extractor = keras.Model(inputs=model.inputs,
                                    outputs=[layer.output for layer in model.layers])
            feature_extractor.compile()
            middle_layers_outputs = feature_extractor(x_train)
            #Fairly huge to print
            #print(f"Middle layers output for layer 1 {middle_layers_outputs[0]}")

            #get_weights already gives youu two arrays, first is actual weights, second,if it exists, are bias(non-treinable weights)
            weights = [layer.get_weights() for layer in model.layers]
            # for i in range(len(model.layers)):
            #         print(f'For Layer {i} got weights {model.layers[i].get_weights()}')

            #Could be posted once
            json_model = self.model.to_json()

            print('Post to aggregator')
            #TODO:Require all of this data in a single JSON file, accompany ID and epoch
            #res = requests.post(url, json = data)
            #print('Post status:',res)
        print("End epoch {} of training;".format(epoch))



model.fit(dataset, batch_size=BATCH_SIZE, epochs=EPOCHS
          , callbacks= [DataAggregateCallback()], validation_data=(x_val, y_val),)
model.evaluate(x_test, y_test, batch_size=128, verbose=0)

