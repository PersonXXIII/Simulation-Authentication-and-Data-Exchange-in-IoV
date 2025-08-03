from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential

class TwinManager:
    def __init__(self):
        # Initialize the DigitalTwinsClient
        self.service_client = DigitalTwinsClient(
            "https://SimulationForIoV.api.wcus.digitaltwins.azure.net",
            DefaultAzureCredential()
        )

    def fetch_the_twin_data_only(self, twin_id):
        try:
            # print(f"Fetching data for twin with ID: {twin_id}...")

            # Get the twin by its ID
            twin = self.service_client.get_digital_twin(twin_id)

            # Enhanced display of twin data
            twin_data = {
                "ID": twin["$dtId"],
                "Name": twin.get("Name", "N/A"),
                "Model": twin.get("Model", "N/A"),
                "VIN": twin.get("VIN", "N/A"),
                "PublicKey": twin.get("PublicKey", "N/A"),
                "PrivateKey": twin.get("PrivateKey", "N/A"),
                "Metadata": twin.get("$metadata", {})
            }
            # print(twin_data)
            return twin_data

        except Exception as e:
            print(f"Error retrieving twin data: {e}")


