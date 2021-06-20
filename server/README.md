# Server Documentation
![alt](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)  ![alt](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) 

The following environment variables can be used to configure this component:

- SELF_PORT: Defaults to 8000
- DATABASE_HOST: Defaults to timescaledb
- DATABASE_PORT: Defaults to 5432
- DATABASE_NAME: Defaults to nntracker
- DATABASE_USER: Defaults to root
- DATABASE_PASSWORD: Defaults to postgres
- GRAFANA_BASE_URL: Used to embed grafana views,defaults to http://localhost:3000
- DEPLOYER_BASE_URL: Used to build deployer requests, defaults to http://tracker-deployer:7000

The following arguments are used in a configuration file to create a simulation/simulations:

- name : The simulation's name
    - String, required
- dataset_train : A url to the training dataset
    - String, not required when local files are used
- dataset_test : A url to the test dataset
    - String, not required when local files are used
- dataset_val : A url to the validation dataset
    - String, not required when local files are used
- batch_size : The simulation's batch size
    - Integer, required
- total_epochs : How many epochs the simulation will run
    - Integer, required
- epoch_period : The period in which our service will collect the simulation's data
    - Integer, required
- optimizers : Optimizers to be used in each simulation and their configurations
    - List of dictionaries, at least 1 required
    - Optimizer dictionary:
        - optimizer : A string with the class' name
        - conf : A dictionary with the necessary configuration for this specific optimizer
- loss_function : Loss functions to be used in each simulation and their configurations
    - List of dictionaries, at least 1 required
    - Loss function dictionary:
        - loss_function : A string with the class' name
        - conf : A dictionary with the necessary configuration for this specific loss function
- learning_rates : Learning rates to be used in each simulation
    - List of floats, at least 1 required
- k-fold_validation : How many times the simulation will split
    - Integer, not required
- k-fold_tag: Identification for all simulations caused by the split
    - String, required when "k-fold_validation" is set
- extra-metrics : Additional metrics to be gathered from each simulation epoch
    - List of dictionaries, required but can be empty ( [] )
    - Extra metric dictionary:
        - metric : A string with the class' name
        - conf : A dictionary with the necessary configuration for this specific metric
- tags : Identifications for all simulations
    - List of strings, not required
- train_feature_name : Key name given in the map stored in the .npz training dataset file corresponding to the dataset features
    - String, required if datasets use .npz format
- train_label_name : Key name given in the map stored in the .npz training dataset file corresponding to the dataset label
    - String, required if datasets use .npz format
- test_feature_name : Key name given in the map stored in the .npz test dataset file corresponding to the dataset features
    - String, required if datasets use .npz format
- test_label_name : Key name given in the map stored in the .npz test dataset file corresponding to the dataset label
    - String, required if datasets use .npz format
- val_feature_name : Key name given in the map stored in the .npz validation dataset file corresponding to the dataset features
    - String, required if datasets use .npz format
- val_label_name : Key name given in the map stored in the .npz validation dataset file corresponding to the dataset label
    - String, required if datasets use .npz format
- label_column : Name of the column to be used as a feature vector
    - String, required if datasets use any format besides .npz

In the previous list more than one simulations are created when the "optimizers", "loss_functions" or "learning_rates" have more than one value or when "k-fold_validation" is bigger than 1.

Datasets can have the following formats:
- .npz
- .csv
- .pickle (pandas)
- .zip (pandas)
- .arff
- .json

The optimizer classes can be found [here](https://www.tensorflow.org/api_docs/python/tf/keras/optimizers).

The loss function classes can be found [here](https://www.tensorflow.org/api_docs/python/tf/keras/losses).

The metric classes can be found [here](https://www.tensorflow.org/api_docs/python/tf/keras/metrics).

An example of this configuration file can be found in the file [server_conf.json](server_conf.json). 