from flask import Flask, request
from celery import Celery
import psycopg2
import sys
import uuid
import psycopg2.extras
import datetime

# call it in any place of your program
# before working with UUID objects in PostgreSQL
psycopg2.extras.register_uuid()

conn = None
if "celery" in sys.argv[0]:
    try:
        conn = psycopg2.connect(
            host="timescaledb",
            database="nntracker",
            user="root",
            password="postgres",
            port="5432",
            connect_timeout=4
        )
    except Exception as error:
        print("Error connecting to db: ", error, file=sys.stderr)
        print("Error type: ", type(error), file=sys.stderr)


app = Flask(__name__)

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.route('/update', methods=['POST'])
def update_simulation():
    logger.info("/update called")
    print("/update called", file=sys.stderr)
    simulation_data = request.get_json(force=True)

    result = update_data_sent.delay(simulation_data)
    return 'All good'

@app.route('/finish', methods=['POST'])
def finish_simulation():
    simulation_data = request.get_json()
    print("/finish called", file=sys.stderr)

    result = finish_data_sent.delay(simulation_data)
    return 'All good'

@app.route('/send_error', methods=['POST'])
def send_error_simulation():
    logger.info("/send_error called")
    print("/send_error called", file=sys.stderr)
    simulation_data = request.get_json(force=True)


    result = send_error.delay(simulation_data)
    return 'All good'

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)

    return celery


app.config.update(
    broker_url = 'redis://redis:6379',
    result_backend = 'redis://redis:6379',

    task_serializer = 'json',
    result_serializer = 'json',
    accept_content = ['json'],
    timezone = 'Europe/Lisbon',
    enable_utc = True,
)
celery = make_celery(app)


def check_connection():
    global conn
    if conn.closed:
        print("Connection was closed ", file=sys.stderr)
        print("Reconnecting... ", file=sys.stderr)
        try:
            conn = psycopg2.connect(
                host="timescaledb",
                database="nntracker",
                user="root",
                password="postgres",
                port="5432",
                connect_timeout=4
            )
        except Exception as error:
            print("Error connecting to db: ", error, file=sys.stderr)
            print("Error type: ", type(error), file=sys.stderr)


@celery.task()
def update_data_sent(json_file):
    for _ in range(2):
        check_connection()

        try:
            curr = conn.cursor()
            logger.info('update starting')
            simid, epoch, weights, loss, accuracy, val_loss, val_accuracy, metrics = process_data(json_file)

            sqlWeights = "INSERT INTO Weights(epoch,layer_index,layer_name,sim_id,weight,time) VALUES(%s,%s,%s,%s,%s,%s)"
            sqlEpoch = "INSERT INTO Epoch_values(epoch,sim_id,loss,accuracy,time,val_loss, val_accuracy) VALUES(%s,%s,%s,%s,%s,%s,%s)"
            sqlExtraMetrics = "INSERT INTO Extra_metrics(epoch,sim_id,value,metric,time) VALUES(%s,%s,%s,%s,%s)"

            for w in weights.keys():
                index = w
                curr.execute(sqlWeights, (str(epoch), index, "0", simid, weights[w], datetime.datetime.now()))

            for metric in metrics.keys():
                curr.execute(sqlExtraMetrics, (str(epoch), simid, metrics[metric], metric, datetime.datetime.now()))

            curr.execute(sqlEpoch, (epoch, simid, loss, accuracy, datetime.datetime.now(), val_loss, val_accuracy))
            conn.commit()
            curr.close()
            break
        except Exception as error:
            print("Error executing queries on /update task with error: ", error, file=sys.stderr)
            print("Error type: ", type(error), file=sys.stderr)
            print("If it is the first time this error message is shown a retry is being done ", type(error), file=sys.stderr)

    return None


def process_data(data_dict):
    logger.info(type(data_dict['weights']))
    for i in range(len(data_dict['weights'])):
        layer_data = data_dict['weights'][i]

    weights = {str(i) : data_dict['weights'][i][0] if data_dict['weights'][i] != [] else [] for i in range(len(data_dict['weights'])) }

    loss = data_dict['logs']['loss']
    accuracy = data_dict['logs']['accuracy']
    val_loss = data_dict['logs']["val_loss"]
    val_accuracy = data_dict['logs']["val_accuracy"]

    metrics = {}
    for metric in data_dict['logs'].keys():
        if metric not in ['loss','accuracy','val_accuracy','val_loss']:
            metrics[metric] = data_dict['logs'][metric]

    epoch = data_dict['epoch']
    simid = uuid.UUID(int=int(data_dict['sim_id']))

    return simid, epoch, weights, loss, accuracy, val_loss, val_accuracy, metrics


@celery.task()
def finish_data_sent(json_file):
    for _ in range(2):
        check_connection()

        try:
            curr = conn.cursor()
            simid, epoch, weights, loss, accuracy,val_loss, val_accuracy, metrics = process_data(json_file)
            sqlWeights = "INSERT INTO Weights(epoch,layer_index,layer_name,sim_id,weight,time) VALUES(%s,%s,%s,%s,%s,%s)"
            sqlEpoch = "INSERT INTO Epoch_values(epoch,sim_id,loss,accuracy,time,val_loss,val_accuracy) VALUES(%s,%s,%s,%s,%s,%s,%s)"
            sqlUpdate = "UPDATE simulations SET isdone=TRUE, isrunning=FALSE WHERE id=%s"
            sqlExtraMetrics = "INSERT INTO Extra_metrics(epoch,sim_id,value,metric,time) VALUES(%s,%s,%s,%s,%s)"

            for w in weights.keys():
                index = w
                curr.execute(sqlWeights, (str(epoch), index, "0", simid, weights[w], datetime.datetime.now()))

            for metric in metrics.keys():
                curr.execute(sqlExtraMetrics, (str(epoch), simid, metrics[metric], metric, datetime.datetime.now()))

            curr.execute(sqlEpoch, (epoch, simid, loss, accuracy, datetime.datetime.now(),val_loss, val_accuracy))
            curr.execute(sqlUpdate,(simid,))
            conn.commit()
            curr.close()
            break
        except Exception as error:
            print("Error executing queries on /finish task with error: ", error, file=sys.stderr)
            print("Error type: ", type(error), file=sys.stderr)

    return None

@celery.task()
def send_error(json_file):
    for _ in range(2):
        check_connection()

        try:
            curr = conn.cursor()
            simid = uuid.UUID(int=int(json_file["id"]))
            error_text = json_file["error"]
            sqlUpdate = "UPDATE simulations SET isrunning=False, error_text=%s WHERE id=%s"
            curr.execute(sqlUpdate,(error_text, simid))
            conn.commit()
            curr.close()
            break
        except Exception as error:
            print("Error executing queries on /send_error task with error: ", error, file=sys.stderr)
            print("Error type: ", type(error), file=sys.stderr)

    return None