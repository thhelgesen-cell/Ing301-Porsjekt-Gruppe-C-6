import time
import math
import requests
import datetime
import logging

log_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")

import common

TEMPERATURE_SENSOR_CLIENT_SLEEP_TIME = 4
TEMP_RANGE = 40


class SensorClient:
    """
    Sensor client representing the physical temperature sensor
    in the house and reporting temperature to the cloud service
    """

    def __init__(self, did):
        self.did = did

    def do_measurement(self) -> common.SensorMeasurement:
        """
        Simulate reading a temperature
        """
        logging.info(f"Sensor {self.did} measuring")

        temp = round(math.sin(time.time() / 10) * TEMP_RANGE, 1)

        logging.info(f"Sensor measured {self.did}: {temp}")

        # 🔑 value skal være float (ikke string)
        measurement = common.SensorMeasurement(
            datetime.datetime.now().isoformat(),
            temp,
            "°C"
        )

        return measurement

    def put_measurement(self, m: common.SensorMeasurement) -> requests.Response:
        """
        Send measurement til API
        """
        logging.info(f"Sensor client {self.did} update starting")

        url = f"{common.BASE_URL}/smarthouse/sensor/{self.did}/current"

        payload = {
            "timestamp": m.timestamp,
            "value": float(m.value),  # sikker på riktig type
            "unit": m.unit
        }

        try:
            response = requests.put(url, json=payload)

            logging.info(
                f"Sensor client {self.did} response: {response.status_code}"
            )

            return response

        except Exception as e:
            logging.error(f"Sensor client error: {e}")
            return None

    def run(self):
        """
        Loop: measure + send
        """
        while True:
            m = self.do_measurement()
            self.put_measurement(m)
            time.sleep(TEMPERATURE_SENSOR_CLIENT_SLEEP_TIME)


if __name__ == '__main__':
    sensor = SensorClient(common.TEMPERATURE_SENSOR_DID)
    sensor.run()