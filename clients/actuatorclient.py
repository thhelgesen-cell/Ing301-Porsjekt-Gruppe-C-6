import time
import requests
import logging

log_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")

import common

LIGHTBULB_CLIENT_SLEEP_TIME = 4


class ActuatorClient:
    """
    Actuator client representing the physical light bulb in the house
    using the cloud service to set its state
    """

    def __init__(self, did):
        self.did = did
        self.state = None  # siste kjente state

    def get_state(self):
        """
        Fetch current actuator state from API
        """
        logging.info(f"Actuator Client {self.did} retrieving state")

        url = f"{common.BASE_URL}/smarthouse/actuator/{self.did}/state"

        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                return data.get("state")

            logging.warning(f"Failed to get state: {response.status_code}")
            return None

        except Exception as e:
            logging.error(f"Actuator client error: {e}")
            return None

    def apply_state(self, new_state):
        """
        Simulate applying state to the physical device
        """
        if new_state == self.state:
            return  # ingen endring

        logging.info(f"Actuator {self.did} new state: {new_state}")

        if isinstance(new_state, bool):
            if new_state:
                logging.info("[LIGHT BULB] ON")
            else:
                logging.info("[LIGHT BULB] OFF")
        else:
            logging.info(f"[LIGHT BULB] Brightness: {new_state}")

        self.state = new_state

    def run(self):
        """
        Loop: fetch state → apply if changed
        """
        while True:
            new_state = self.get_state()

            if new_state is not None:
                self.apply_state(new_state)

            time.sleep(LIGHTBULB_CLIENT_SLEEP_TIME)


if __name__ == '__main__':
    actuator = ActuatorClient(common.LIGHT_BULB_ACTUATOR_DID)
    actuator.run()