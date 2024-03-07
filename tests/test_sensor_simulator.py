import sys
from pathlib import Path

# Adiciona o diretório pai ao sys.path para que possamos importar sensor_simulator
sys.path.append(str(Path(__file__).parent.parent))

import os
import time

import paho.mqtt.client as mqtt
import pytest
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from paho import mqtt

from sensor_simulator import SolarRadiationSensorSimulator
import datetime
import paho.mqtt.client as paho

load_dotenv()

# Configurações do MQTT
broker_address = os.getenv("BROKER_ADDR")
port = 8883
topic = "solar_sensor_test"
username = os.getenv("HIVE_USER")
password = os.getenv("HIVE_PSWD")


DATABASE_URL = os.getenv("MONGO_URI")
DATABASE_NAME = "sensors_data"
COLLECTION_NAME = "solar_data_test"

received_messages = []

# Callback para quando uma mensagem é recebida do broker
def on_message(client, userdata, message):
    received_messages.append((message.topic, message.payload.decode()))


# Setup do cliente MQTT para teste
@pytest.fixture(scope="module")
def mqtt_client():
    client = paho.Client(paho.CallbackAPIVersion.VERSION2, "test_subscriber")
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(username, password)
    client.on_message = on_message
    client.connect(broker_address, port)
    client.subscribe(topic)
    client.loop_start()
    yield client
    client.loop_stop()
    client.disconnect()


@pytest.fixture(scope="module")
def db_client():
    client = MongoClient(DATABASE_URL)
    yield client
    client.close()


# Testa se a mensagem é recebida corretamente
def test_message_reception(mqtt_client):
    solar_sensor = SolarRadiationSensorSimulator(topic)
    solar_sensor.publish_data(mqtt_client)

    # Espera breve para garantir a recepção da mensagem
    time.sleep(1)

    assert len(received_messages) > 0, "Nenhuma mensagem foi recebida."
    assert (
        received_messages[-1][0] == topic
    ), f"Mensagem recebida no tópico incorreto: {received_messages[-1][0]}"

    # Validação básica dos dados, mais verificações podem ser adicionadas conforme a necessidade
    received_data = received_messages[-1][1]
    assert "W/m2" in received_data, "O formato dos dados recebidos está incorreto."

    received_messages.clear()  # Limpa as mensagens recebidas após o teste


# Testa a taxa de disparo das mensagens
def test_message_rate(mqtt_client):
    received_messages.clear()  # Limpa as mensagens recebidas anteriormente

    solar_sensor = SolarRadiationSensorSimulator(topic)
    start_time = time.time()

    # Publica duas mensagens com intervalo de 2 segundos
    solar_sensor.publish_data(mqtt_client)
    time.sleep(2)
    solar_sensor.publish_data(mqtt_client)

    # Espera breve para garantir a recepção das mensagens
    time.sleep(1)

    assert len(received_messages) >= 2, "Menos de duas mensagens foram recebidas."
    time_diff = time.time() - start_time
    assert (
        time_diff > 2 and time_diff < 4
    ), "A taxa de disparo das mensagens está fora do esperado."

    received_messages.clear()  # Limpa as mensagens recebidas após o teste


def test_database_integration(db_client, mqtt_client):
    # Conectar ao banco de dados e à coleção
    db = db_client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Limpar a coleção para o teste
    collection.delete_many({})

    # Dados simulados para publicação
    test_data = {
        "data": "100 W/m2",
        "topic": topic,
        "created_at": datetime.datetime.now(),
    }

    db_client[DATABASE_NAME][COLLECTION_NAME].insert_one(test_data) 

    # Aguardar um breve período para garantir o processamento
    time.sleep(2)  # Ajuste o tempo conforme necessário

    # Verificar se os dados foram armazenados no banco de dados
    stored_data = collection.find_one({"topic": topic})

    assert stored_data is not None, "Nenhum dado foi armazenado no banco de dados."
    assert (
        stored_data["data"] == "100 W/m2"
    ), "Os dados armazenados no banco de dados estão incorretos."

    # Limpar dados de teste da coleção após o teste
    collection.delete_many({})

    received_messages.clear()  # Limpa as mensagens recebidas após o teste
