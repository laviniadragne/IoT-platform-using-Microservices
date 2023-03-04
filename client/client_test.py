import json
import paho.mqtt.client as mqtt
import time
import json


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc), flush = True)


if __name__ == '__main__':
    broker_client = mqtt.Client()
    broker_client.on_connect = on_connect

    broker_client.connect("localhost", 1883, 60)

    topics = ["UPB/RPi_1", "Dorinel/Zeus", "UPB/GAS", "UPB/MONGO"]
    payloads = [{"BAT" : 99, "HUMID" : 40, "PRJ " : "SPRC", "TMP" : 25.3 , "status" : "OK" , "timestamp" : "2019-11-26T03:54:20+03:00"}, \
                {"Alarm" : 0 , "AQI " : 12 , "RSSI " : 1500 }, \
                {"BAT" : 4, "CO" : 20, "HAM" : 18, "NO2" : 22, "O2" : 27, "TC" : 30}, \
                {"BAT" : 20, "HUM" : 17, "TC" : 14}]

    broker_client.loop_start()

    for _ in range(30):
        broker_client.publish(topics[0], json.dumps(payloads[0]))
        time.sleep(1)
        broker_client.publish(topics[1], json.dumps(payloads[1]))
        time.sleep(1)
        broker_client.publish(topics[2], json.dumps(payloads[2]))
        time.sleep(1)
        broker_client.publish(topics[3], json.dumps(payloads[3]))
        time.sleep(1)


    broker_client.loop_stop()
    broker_client.disconnect()
