
BOX_params = "box_params"
BME680 = "bme680"
SGP30 = "sgp30"


INDEX = "index"
TIME = "timestamp"

BOX_ID = "box_id"
IAQ = "iaq"
IAQ_ACC = "iaq_acc"
TEMP = "temperature"
HUM = "humidity"
PRES = "pressure"
GAS = "gas"
tVOC = "tVOC"
eCO2 = "eCO2"

BOX_data = {BOX_ID: 0}
BME680_data = {IAQ: 0, IAQ_ACC: 0, TEMP: 0, HUM: 0, PRES: 0, GAS: 0}
SGP30_data = {tVOC: 0, eCO2: 0}

moxbox_stream = {BOX_params: BOX_data, BME680: BME680_data, SGP30: SGP30_data}
