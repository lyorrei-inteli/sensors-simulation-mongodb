import abc
import math
import random
import time

class SensorSimulator(abc.ABC):
    def __init__(self, topic):
        self.topic = topic

    @abc.abstractmethod
    def simulate_data(self):
        pass

    def publish_data(self, client):
        data = self.simulate_data()
        client.publish(self.topic, data)
        print(f"Publicado no tópico {self.topic}: {data}")

class SolarRadiationSensorSimulator(SensorSimulator):
    def simulate_data(self):
        hour_of_day = time.localtime().tm_hour
        radiation_value = self.simulate_solar_radiation(hour_of_day)
        return f"{radiation_value:.2f} W/m2"

    def simulate_solar_radiation(self, hour):
        radians = hour / 24.0 * 2.0 * math.pi
        base_radiation = max(0, math.sin(radians))
        radiation = base_radiation * 1280
        variation = random.uniform(-50, 50)
        return max(0, min(1280, radiation + variation))
