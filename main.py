
import dask.dataframe as dd
import pandas as pd
from bokeh.io import output_file, show
from bokeh.layouts import row, widgetbox, column, layout
from bokeh.models.widgets import Div, Dropdown, Select, TextInput
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import LinearAxis, Range1d
from bokeh.plotting import curdoc, figure
from bokeh.models import ColumnDataSource, HoverTool
from os import path

from utils import *

sensor_select = Select(title='Sensor', value=get_box_ls()[0], options=get_box_ls())
ddf = dd.read_csv(path.join(path.join(data_path, sensor_select.value), sensor_select.value + '*.csv'),
                  delimiter="\t", parse_dates=['timestamp']).set_index(TIME)
ddf.compute()
dates_ls = []


def get_dates():
    moxbox_folder = os.path.join(data_path, sensor_select.value)
    files = [f for f in os.listdir(moxbox_folder) if os.path.isfile(os.path.join(moxbox_folder, f))]
    dates_ls_temp = [f.split("_")[1].split(".")[0] for f in files]
    dates_ls_temp.sort()
    return dates_ls_temp


def get_ddf():
    global ddf
    curr_path = path.join(data_path, sensor_select.value)
    ddf = dd.read_csv(path.join(curr_path, sensor_select.value + '*.csv'),
                      delimiter="\t", parse_dates=['timestamp']).set_index(TIME)


def filter_df():
    global ddf
    # Select time period
    start = pd.to_datetime(date_start_select.value)
    end = pd.to_datetime(date_end_select.value) + pd.to_timedelta(1, 'D')
    ddf_filter = ddf[start:end]
    
    # Resample dataframe
    #print(fz_select.value)
    resample_fz = sample_fz[fz_select.value]
    ddf_filter = ddf_filter.resample(resample_fz).mean()

    # TODO : change the temp with right column to filter
    ddf_filter = ddf_filter[ddf_filter[BOX_params+'_'+BOX_ID].notnull()]

    df_update = ddf_filter.compute()
    df_update.index.rename(TIME, inplace=True)
    return df_update


fz_select = Select(title='Period', value=sample_fz_ls[0], options=sample_fz_ls)
date_start_select = Select(title='Start date', value=get_dates()[0], options=get_dates())
date_end_select = Select(title='End date (+24h)', value=get_dates()[-1], options=get_dates())

controls = widgetbox([sensor_select, fz_select, date_start_select, date_end_select], width=200)

#GRAPHS
df = filter_df()
source = ColumnDataSource(df)

hover = HoverTool(
    tooltips=[
        ('timestamp', '@timestamp{%F %T}'),
        ('value', '$y'),
    ],
    formatters={
        'timestamp': 'datetime',
    },
)
p_tvoc = figure(plot_height=int(int(0.35 * plot_height)), plot_width=plot_width, tools=tool_str)
p_co2 = figure(plot_height=int(int(0.35 * plot_height)), plot_width=plot_width, tools=tool_str, x_range=p_tvoc.x_range)

p_temp = figure(plot_height=int(int(0.3 * plot_height)), plot_width=int(plot_width/2), tools=tool_str, x_range=p_tvoc.x_range)
p_rh = figure(plot_height=int(int(0.3 * plot_height)), plot_width=int(plot_width/2), tools=tool_str, x_range=p_tvoc.x_range)

p_tvoc.toolbar.logo = None
p_co2.toolbar.logo = None
p_temp.toolbar.logo = None
p_rh.toolbar.logo = None

for col in list(df.columns):
    try:
        color = color_id[col.split('_')[0]]
    except KeyError:
        pass

    if col.find(tVOC) != -1:
        p_tvoc.line(x=TIME, y=col, source=source, legend=dict(value=col), name=col, color=color)
    elif col.find(CO2) != -1:
        p_co2.line(x=TIME, y=col, source=source, legend=dict(value=col), name=col, color=color)
    elif col.find(TEMP) != -1:
        color = "red"
        p_temp.line(x=TIME, y=col, source=source, legend=dict(value=col), name=col, color=color)
    elif col.find(HUM) != -1:
        color = "green"
        p_rh.line(x=TIME, y=col, source=source, legend=dict(value=col), name=col, color=color)

p_tvoc.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
p_tvoc.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
p_tvoc.xaxis.major_label_text_font_size = '0pt'

y_fmt = ["%F"]
h_fmt = ["%d/%m %T"]
p_co2.xaxis.formatter = DatetimeTickFormatter(seconds=h_fmt, minsec=h_fmt, minutes=h_fmt,
                                               hourmin=y_fmt, hours=y_fmt, days=y_fmt,
                                               months=y_fmt, years=y_fmt)
p_temp.xaxis.formatter = DatetimeTickFormatter(seconds=h_fmt, minsec=h_fmt, minutes=h_fmt,
                                               hourmin=y_fmt, hours=y_fmt, days=y_fmt,
                                               months=y_fmt, years=y_fmt)
p_rh.xaxis.formatter = DatetimeTickFormatter(seconds=h_fmt, minsec=h_fmt, minutes=h_fmt,
                                               hourmin=y_fmt, hours=y_fmt, days=y_fmt,
                                               months=y_fmt, years=y_fmt)

p_tvoc.legend.location = "top_left"
p_tvoc.legend.click_policy = "hide"

p_co2.legend.location = "top_left"
p_co2.legend.click_policy = "hide"

p_rh.legend.location = "top_left"
p_rh.legend.click_policy = "hide"

p_temp.legend.location = "top_left"
p_temp.legend.click_policy = "hide"

#p_temp.xaxis.major_tick_line_color = None
#p_temp.xaxis.minor_tick_line_color = None

p_tvoc.add_tools(hover)
p_co2.add_tools(hover)
p_temp.add_tools(hover)
p_rh.add_tools(hover)

#DIVS
div = Div(text="""  <h1 style="text-align: left;"> <img src="Groupe_SEB_-_Logo.svg" alt="logo_seb" height="50px"> DT481 - MOx Data Processing Dashboard</h1>""", width=plot_width, height=50)

def auto_update():
    print("auto-update")
    get_ddf()
    update()

def update_sensor_data():
    global dates_ls
    dates_ls = get_dates()
    date_start_select.options = dates_ls
    date_end_select.options = dates_ls
    date_start_select.value = dates_ls[0]
    date_end_select.value = dates_ls[-1]
    get_ddf()
    update()


def update_date_start():
    global dates_ls
    dates_ls = get_dates()
    if (date_start_select.value in dates_ls) and (date_end_select.value in dates_ls):
        if dates_ls.index(date_start_select.value) > dates_ls.index(date_end_select.value):
            date_end_select.value = dates_ls[-1]
        print("date update")
        update()


def update_date_end():
    global dates_ls
    dates_ls = get_dates()
    if (date_start_select.value in dates_ls) and (date_end_select.value in dates_ls):
        if dates_ls.index(date_start_select.value) > dates_ls.index(date_end_select.value):
            date_start_select.value = dates_ls[0]
        print("date update")
        update()


def update():
    print("update")
    df_update = filter_df()
    df_update_dict = df_update.to_dict(orient="list")
    df_update_dict[TIME] = list(df_update.index.values)
    # source.data = {
    #     TIME: df_update.index,
    #     TEMP: df_update[TEMP],
    #     HUM: df_update[HUM],
    #     GAS: df_update[GAS],
    #     PRES: df_update[PRES],
    # }
    source.data = df_update_dict
    sensor_select.options = get_box_ls()


sensor_select.on_change('value', lambda attr, old, new: update_sensor_data())
fz_select.on_change('value', lambda attr, old, new: update())
date_start_select.on_change('value', lambda attr, old, new: update_date_start())
date_end_select.on_change('value', lambda attr, old, new: update_date_end())

l = layout([
    [div],
    [controls, [p_tvoc, p_co2, [p_temp, p_rh]]]
])

update()

curdoc().add_root(l)
curdoc().title = "DT481 - Mox Sensor Dash Board"

curdoc().add_periodic_callback(auto_update, 30000)
output_file("MoxBoxServer.html")
show(l)
