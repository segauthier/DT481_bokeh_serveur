from os import path
import os

# Manual dirty import from the template use in the Wipy board
# lib_path = os.path.join(os.path.dirname(sys.path[0]), "DT481_socket_server\wipy\lib")
# sys.path.insert(0, lib_path)
# from box_data_template import *

# The box data file should be identical to the one used in the wipy.lib folder
from box_data_template import *

plot_width = 1000
plot_height = 500

tool_str = 'pan,box_zoom,reset'

scale_factor = 5/100
scale_up = 1+scale_factor
scale_down = 1-scale_factor

color_id = {BME680: "navy", SGP30: "crimson", CCS811: "seagreen"}

dir_path = path.dirname(path.realpath(__file__))
data_path = path.join(dir_path, "data")

sample_fz = {"1s": "1S", "10s": "10S", "30s": "30S", "1min": "1T", "5min": "5T",
             "10min": "10T", "30min": "30T", "1h": "1H", "4h": "4H", "1j": "1D", "1sem": "1W"}
sample_fz_ls = list(sample_fz.keys())



# CONTROLS
def get_box_ls():
    box_ls = []
    for f in os.listdir(data_path):
        # remove the hidden folders
        if f[0]!='.':
            box_ls.append(f)           
    return box_ls



BME680_data = {IAQ: 0, IAQ_ACC: 0, TEMP: 0, HUM: 0, PRES: 0, GAS: 0}
box_data = {BOX_ID: 0, BME680: BME680_data}

dir_path = path.dirname(path.realpath(__file__))
data_path = path.join(dir_path, "data")


sample_fz = {"1s": "1S", "10s": "10S", "30s": "30S", "1min": "1T", "5min": "5T",
             "10min": "10T", "30min": "30T", "1h": "1H", "4h": "4H", "1j": "1D", "1sem": "1W"}
sample_fz_ls = list(sample_fz.keys())


# CONTROLS
def get_box_ls():
    box_ls = []
    for (dirpath, dirnames, filenames) in os.walk(data_path):
        if (dirpath == data_path):
            box_ls = dirnames.copy()
    return box_ls

