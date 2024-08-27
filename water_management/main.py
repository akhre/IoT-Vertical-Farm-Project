import logging
import time
from water_manager import *


logging.basicConfig(level=logging.INFO)
SERVICE_NAME = "water_management"
SERVICE_HOST = "water_management"
# SERVICE_RNET = "127.0.0.1"
SERVICE_RNET = "0.0.0.0"
SERVICE_PORT = 8083


def main():

    logging.info("Performing tasks...")
    sensor_retriever = SensorDataRetriever()
    catalog = CatalogIntegration()

    catalog_data = catalog.fetch_plant_info()
    farm, optimal_values_map = Farm.initialize_from_catalog(catalog_data)

    processed_data = DataProcessor.process_sensor_data(farm, sensor_retriever, optimal_values_map)

    # in the scope of water management we notify user, activate the water_pump in the each shelf and update the catalog
    notifier = Notifier()
    notifier.tasks(processed_data)


if __name__ == "__main__":

    logging.info("Registering Water Management...")
    registered = False
    sm = ServiceManager()
    while not registered:
        registered = sm.service_registry(SERVICE_NAME, SERVICE_HOST, SERVICE_PORT)
        time.sleep(3)
    logging.info("Service registered...")


    server = Serv()
    server.start_rest(SERVICE_RNET, SERVICE_PORT)
    
    # for this manager, checking every 30 minutes would be sufficient since
    # moisture may take some time to reflect in the sensor data
    # also for user to have time to fill the water tank
    minutes = 30
    logging.info("sleep for rasp to register and values come in...")
    init_sleep = 10
    time.sleep(init_sleep*60)
    while True:
        try:
            main()
            logging.info(f"Performed Water Management Tasks, sleep for {minutes} minutes...")
            time.sleep(minutes*60)
            # time.sleep(10)
        except Exception as e:
            logging.info("Error occurred during Water Management tasks.")
            logging.info(str(e))

        time.sleep(30)