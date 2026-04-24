import requests
import common


class SmartHouseApp:

    def __init__(self):
        self.sensor_did = common.TEMPERATURE_SENSOR_DID
        self.actuator_did = common.LIGHT_BULB_ACTUATOR_DID
        self.base_url = common.BASE_URL

    # -------------------------
    # ACTUATOR
    # -------------------------
    def get_bulb_state(self) -> str:
        url = f"{self.base_url}/smarthouse/actuator/{self.actuator_did}/state"

        try:
            response = requests.get(url)

            if response.status_code == 200:
                state = response.json().get("state")
                return "on" if state else "off"

        except Exception as e:
            print(f"Error: {e}")

        return "unknown"

    def update_bulb_state(self, new_state: str):
        url = f"{self.base_url}/smarthouse/actuator/{self.actuator_did}/state"

        payload = {
            "state": True if new_state == "on" else False
        }

        try:
            return requests.put(url, json=payload)

        except Exception as e:
            print(f"Error: {e}")
            return None

    # -------------------------
    # SENSOR
    # -------------------------
    def get_temperature(self):
        url = f"{self.base_url}/smarthouse/sensor/{self.sensor_did}/current"

        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                return data.get("value"), data.get("unit")

        except Exception as e:
            print(f"Error: {e}")

        return None, None

    # -------------------------
    # MENU
    # -------------------------
    def run(self):

        while True:
            print("\n---- SmartHouse App ----")
            print("1. Slå av/på lys")
            print("2. Vis temperatur")
            print("3. Vis lys status")
            print("4. Avslutt")

            choice = input(">>> ")

            if choice == "1":
                current = self.get_bulb_state()
                print(f"Nåværende: {current}")

                new_state = "off" if current == "on" else "on"

                self.update_bulb_state(new_state)

                print(f"Ny status: {self.get_bulb_state()}")

            elif choice == "2":
                value, unit = self.get_temperature()
                print(f"Temperatur: {value} {unit}")

            elif choice == "3":
                print(f"Lys: {self.get_bulb_state()}")

            elif choice == "4":
                print("Avslutter...")
                break


if __name__ == "__main__":
    SmartHouseApp().run()