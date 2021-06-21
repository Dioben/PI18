# Simulation Documentation
![alt](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)    ![alt](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=TensorFlow&logoColor=white)
![alt](https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=Keras&logoColor=white)


## Important Note
This component's target data parser can be configured by setting the PARSER_URL environment variable, which defaults to http://parser:6000



### Format necessary for each file format supported ###

**Note:** For all datasets, non-numeric values are not accepted, and 
because of that, any parameters that require it should be converted
to numeric values.

- .npz \
Each dataset file should be a map stored by using numpy.save(),
where there should be two key-value pairs, the first one should be
a list of features of the dataset and second should be a list of labels
corresponding, it's required that the user remembers which names were
used as keys but there isnt any requirement on what these names should be \
Example: \
*train_dt.npz*
    ```json
        {
        'train_feature' : [feature list]
        'train_label' : [label list]
        }  
    ```
- .csv \
Each dataset file should be a file of csv table where each collumn corresponds
to one of the input parameters of the neural network, with the exception
of one which should correspond to the label.Taking all of this into account
each row of non-label collumns should form a input feature vector to be fed
into the algorithim.
The name determined of the label column should be taken into account for,
but there aren't any requirements on what that name should be. \
Example: \
*train_dt.csv*
    ```json
    f1 | f2 | label
    58   20     1
    12   60     0
    ```

- .arff \
In a similiar manner to .csv file it's also composed of table where each collumns
corresponds to one of the input parameters of the neural network, with the exception
of one which should correspond to the label, corresponding to what should be the
@DATA section of the files, besides that it should also include a header section
describing each collumn attriute by it's name and type.
The name determined of the label column should be taken into account for,
but there aren't any requirements on what that name should be. \
Example: 
    ```json
    @RELATION EXAMPLE
    @ATTRIBUTE label NUMERIC
    @ATTRIBUTE f1 NUMERIC
    @ATTRIBUTE f2 NUMERIC
    @ATTRIBUTE f3 NUMERIC
    @DATA
    1,500,100,200
    2,100,700,150
    0,200,400,250
    ```
- .json \
Each dataset file should contain a map, where there should contain a number
of key-value pairs corresponding to each one of the inputs that would
constitute a matrix of feature vectors and a key-value pair corresponding 
to the label vector, the key name of the label vector shhould be known by
the user but there aren't any requirements on what that name should be. \
Example: 
    ```json
    {
    "x1" : [134,214,3123],
    "x2" : [1586,245,3123],
    "label" : [0,4,5],
    }
    ```

- pandas (.zip and .pickle) \
Each dataset file should be gotten by using the pandas.to_pickle() function
when converting a pandas dataframe, by using the compression='zip' argument
value or outputing to a .zip file instead of a pickle one it's possible to
obtain a compressed version of the pickled dataframe file.
The user should take into account the names of the collumn in the dataframe
object that corresponds to the label vector, here aren't any requirements 
on what that name should be. \
Example: \
*Pandas Dataframe Instance - train_df*
    ```json
    f1 | f2 | label
    58   20     1
    12   60     0
    ```
    Example of conversion for both both compreessed and uncompressed: \
    pandas.to_pickle(train_df, "./dataset_train.pickle")
    pandas.to_pickle(train_df, "./dataset_train.zip")