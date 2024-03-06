import paho.mqtt.client as paho
from paho import mqtt
from database.setup import connect_to_db
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

broker_address = os.getenv("BROKER_ADDR")
port = 8883
topic = "solar_sensor"
username = os.getenv("HIVE_USER")
password = os.getenv("HIVE_PSWD")

db_client = connect_to_db()
db = db_client["sensors_data"]


def on_message(client, userdata, message):
    print(message)
    decoded_message = message.payload.decode()
    print(f"Recebido: {decoded_message} no tópico {message.topic}")
    solar_data = db["solar_data"]
    solar_data.insert_one(
        {
            "data": decoded_message,
            "topic": message.topic,
            "created_at": datetime.datetime.now(),
        }
    )
    print("Dado inserido no banco de dados")


def on_connect(client, userdata, flags, rc, _):
    print("Conectado com o código de retorno: ", rc)
    client.subscribe(topic)


client = paho.Client(
    paho.CallbackAPIVersion.VERSION2, "python_subscriber", protocol=paho.MQTTv5
)
client.on_connect = on_connect

# Configurações de TLS
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(username, password)

client.on_message = on_message

client.connect(broker_address, port=port)

client.loop_forever()
