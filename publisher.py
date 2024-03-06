from sensor_simulator import SolarRadiationSensorSimulator
import paho.mqtt.client as paho
from paho import mqtt
import time 

from dotenv import load_dotenv
load_dotenv()

import os

broker_address = os.getenv("BROKER_ADDR")
port = 8883
topic = "solar_sensor"
username = os.getenv("HIVE_USER")
password = os.getenv("HIVE_PSWD")

# Inicialização do cliente MQTT
client = paho.Client(paho.CallbackAPIVersion.VERSION2, "python_publisher", protocol=paho.MQTTv5)

# Configurações de TLS
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(username, password)  # Configuração da autenticação

client.connect(broker_address, port)

solar_sensor = SolarRadiationSensorSimulator(topic)

try:
    while True:
        solar_sensor.publish_data(client)
        time.sleep(2)  # Esperar 2 segundos antes da próxima publicação
except KeyboardInterrupt:
    print("Publicação encerrada")
    client.disconnect()
