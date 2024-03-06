import sys
from pathlib import Path

# Adiciona o diretório pai ao sys.path para que possamos importar sensor_simulator
sys.path.append(str(Path(__file__).parent.parent))

import time

import paho.mqtt.client as mqtt
import pytest

from sensor_simulator import SolarRadiationSensorSimulator

# Configurações do MQTT
broker_address = "localhost"
port = 1891  # Porta padrão do MQTT
topic = "solar_sensor_test"

received_messages = []

# Callback para quando uma mensagem é recebida do broker
def on_message(client, userdata, message):
    received_messages.append((message.topic, message.payload.decode()))

# Setup do cliente MQTT para teste
@pytest.fixture(scope="module")
def mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "test_subscriber")
    client.on_message = on_message
    client.connect(broker_address, port, 60)
    client.subscribe(topic)
    client.loop_start()
    yield client
    client.loop_stop()
    client.disconnect()

# Testa se a mensagem é recebida corretamente
def test_message_reception(mqtt_client):
    solar_sensor = SolarRadiationSensorSimulator(topic)
    solar_sensor.publish_data(mqtt_client)
    
    # Espera breve para garantir a recepção da mensagem
    time.sleep(1)

    assert len(received_messages) > 0, "Nenhuma mensagem foi recebida."
    assert received_messages[-1][0] == topic, f"Mensagem recebida no tópico incorreto: {received_messages[-1][0]}"

    # Validação básica dos dados, mais verificações podem ser adicionadas conforme a necessidade
    received_data = received_messages[-1][1]
    assert "W/m2" in received_data, "O formato dos dados recebidos está incorreto."

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
    assert time_diff > 2 and time_diff < 4, "A taxa de disparo das mensagens está fora do esperado."

