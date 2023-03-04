from datetime import datetime
from dotenv import load_dotenv
import os
from influxdb import InfluxDBClient
import json
import paho.mqtt.client as mqtt
import time


load_dotenv()
database = os.getenv('DATABASE_NAME')
brokerHost = os.getenv('BROKER')
serviceDatabaseName = os.getenv('SERVICE_DATABASE')
debugDataFlow = os.getenv('DEBUG_DATA_FLOW')
stack = "sprc3_"

def print_logs(msg):
    if debugDataFlow == "true":
        print(msg, flush = True)


def on_connect(client, userdata, flags, rc):
    print_logs("Connected with result code " + str(rc))


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    topic = msg.topic

    # Obtin statia si locatia
    tokens = topic.split("/")
    location = tokens[0]
    station = tokens[1]

    print_logs("Received a message by topic {location_s}/{station_s}".format(location_s = location, station_s = station))

    # Obtin timestamp-ul
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    timestamp_msg = "NOW"
    if "timestamp" in payload:
        timestamp = payload["timestamp"]
        timestamp_msg = timestamp

    print_logs("Data timestamp is: {timestamp}".format(timestamp = timestamp_msg))

    json_db_payload = []

    # Parsare msg.payload
    for key in payload:
        measurement = station
        if type(payload[key]) == int or type(payload[key]) == float:
            measurement += "." + key
            field_key = key
            field_val = payload[key]
            data = {"measurement": measurement, "tags": {"location": location, "station" : station}, "fields": {field_key: field_val}, "time": timestamp}

            print_logs("{location_s}.{station_s}.{key_s} {value_s}".format(location_s = location, station_s = station, key_s = field_key, value_s = field_val))

            # Append-uiesc payload-ul
            json_db_payload.append(data)


    # Scriu in baza de date
    try:
        database_client.write_points(points = json_db_payload)
    except Exception as e:
        print_logs("Eroare la scrierea in baza de date")
        print_logs(e)


def create_influx_database():
    # Se creaza baza de date
    serviceDataBase = stack + serviceDatabaseName
    client = InfluxDBClient(host = serviceDataBase, port = 8086, database = database)

    try:
        client.create_database(database)
        print_logs("S-a creat baza de date")
    except Exception as e:
        print_logs("Eroare de creare a bazei de date: " + str(e))
        return None


    client.switch_database(database)
    client.create_retention_policy(name = "new_retention", duration = "INF", replication = 1, database = database)

    return client


def create_broker_mqtt(database_client):
    # Se creaza clientul de mqtt
    broker_client = mqtt.Client(userdata = database_client)
    broker_client.on_connect = on_connect
    broker_client.on_message = on_message

    return broker_client



if __name__ == '__main__':
    # Se creaza baza de date
    database_client = create_influx_database()

    if database_client != None:
        broker_client = create_broker_mqtt(database_client)

        brokerHostName = stack + brokerHost
        broker_client.connect(brokerHostName, 1883, 60)

        broker_client.subscribe('#')

        broker_client.loop_forever()
        broker_client.disconnect()




