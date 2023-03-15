#!./env/bin/python
#!python

from datetime import datetime
import random
import time

import influxdb_client as db
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS


# Configurações do cliente InfluxDB
URL = "http://localhost:8086"
TOKEN = "token"
ORG = "inspermileage"
BUCKET = "trainee"


def main():
    # Condições iniciais
    acceleration = 0.0
    speed = 0.0
    interval = 1.0

    # Cria um cliente do InfluxDB
    with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
        # Cria um cliente assíncrono de escrita
        with client.write_api(write_options=ASYNCHRONOUS) as write_client:
            # Executa indefinidamente
            while True:
                # Itera a velocidade
                speed += acceleration * interval
                acceleration = random.uniform(-1.0, 2.0)

                # Limita a velocidade
                if speed < 0.0:
                    speed = 0.0
                elif speed > 70.0:
                    speed = 70.0

                # Obtém o timestamp atual
                now = datetime.utcnow()
                # Cria um Point com a velocidade
                speedPoint = (
                    db.Point("carro")
                    .tag("roda", "Roda")
                    .field("velocidade", speed)
                    .time(now, db.WritePrecision.MS)
                )
                # Envia para o dado no cliente de escrita
                response = write_client.write(bucket=BUCKET, record=speedPoint)

                # Espera terminar a escrita
                while not response.ready():
                    response.wait()

                # Verifica se houve erro
                if not response.successful():
                    raise Exception("Request not successful!")

                # Log da velocidade
                print(f"\r{now.time()}: {speed:+07.2f} km/h ({acceleration:+.2f})", end="")

                # Espera um tempo entre cada escrita
                time.sleep(interval)


# Inicializa o programa
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
