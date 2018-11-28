
import pandas as pd
from bokeh.io import output_file, show
from bokeh.layouts import row, widgetbox, column, layout
from bokeh.models.widgets import Div, Dropdown, Select, TextInput
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import LinearAxis, Range1d
from bokeh.plotting import curdoc, figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.util import session_id

from os import path


from utils import *

bokeh_key = session_id.generate_session_id()
cmd = r"export BOKEH_SECRET_KEY={}".format(bokeh_key)
print(cmd)

dates_ls = []

sensor_select = Select(title='Sensor', value=get_box_ls()[0], options=get_box_ls())
curr_sensor = sensor_select.value

date_select = Select(title='Date', value=get_dates(curr_sensor)[-1], options=get_dates(curr_sensor))
curr_date = date_select.value

fz_select = Select(title='Period', value=sample_fz_ls[0], options=sample_fz_ls)

df = pd.read_csv(get_csv_file(curr_sensor, curr_date), delimiter="\t", parse_dates=['timestamp']).set_index(TIME)


def get_df():
    global df
    df = pd.read_csv(get_csv_file(curr_sensor, curr_date), delimiter="\t", parse_dates=['timestamp']).set_index(TIME)
    filter_df()


def filter_df():
    global df
    # Resample dataframe
    resample_fz = sample_fz[fz_select.value]
    df = df.resample(resample_fz).mean()
    df = df[df[BOX_params+'_'+BOX_ID].notnull()]
    df.index.rename(TIME, inplace=True)


controls = widgetbox([sensor_select, fz_select, date_select], width=200)

#GRAPHS
filter_df()
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
p_tvoc = figure(plot_height=int(int(0.35 * plot_height)), plot_width=plot_width, tools=tool_str, x_axis_type="datetime")
p_co2 = figure(plot_height=int(int(0.35 * plot_height)), plot_width=plot_width, tools=tool_str, x_range=p_tvoc.x_range, x_axis_type="datetime")

p_temp = figure(plot_height=int(int(0.3 * plot_height)), plot_width=int(plot_width/2), tools=tool_str, x_range=p_tvoc.x_range, x_axis_type="datetime")
p_rh = figure(plot_height=int(int(0.3 * plot_height)), plot_width=int(plot_width/2), tools=tool_str, x_range=p_tvoc.x_range, x_axis_type="datetime")

p_tvoc.toolbar.logo = None
p_co2.toolbar.logo = None
p_temp.toolbar.logo = None
p_rh.toolbar.logo = None

for col in list(df.columns):
    try:
        color = color_id[col.split('_')[0]]
    except KeyError:
        color = "blue"  # CO2 ref
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
                                               hourmin=h_fmt, hours=h_fmt, days=h_fmt,
                                               months=y_fmt, years=y_fmt)
p_temp.xaxis.formatter = DatetimeTickFormatter(seconds=h_fmt, minsec=h_fmt, minutes=h_fmt,
                                               hourmin=h_fmt, hours=h_fmt, days=h_fmt,
                                               months=y_fmt, years=y_fmt)
p_rh.xaxis.formatter = DatetimeTickFormatter(seconds=h_fmt, minsec=h_fmt, minutes=h_fmt,
                                               hourmin=h_fmt, hours=h_fmt, days=h_fmt,
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
logo_path = '/DT481_bokeh_serveur/static/seb_logo.png'
logo_str = '<img src= "{}" alt="{}" height="50px">'.format(logo_path, logo_path)
div_str = """ <h1 style="text-align: left"> {}  &ensp; DT481 - MOx Data Processing Dashboard</h1>""".format(logo_str)


#div_str = """  <h1 style="text-align: left"> DT481 - MOx Data Processing Dashboard</h1> """
div = Div(text=div_str, width=plot_width, height=50)


def auto_update():
    print("auto-update")
    get_df()
    date_select.options = get_dates(curr_sensor)
    update()


def update_sensor():
    global curr_sensor
    global curr_date
    print("sensor update")
    curr_sensor = sensor_select.value
    sensor_select.options = get_box_ls()
    date_select.options = get_dates(curr_sensor)
    curr_date = get_dates(curr_sensor)[-1]
    date_select.value = curr_date
    update()


def update_date():
    global dates_ls
    global curr_date
    print("date update")
    curr_date = date_select.value
    date_select.options = get_dates(curr_sensor)
    update()


def update_fz():
    print("sampling update")
    update()


def update():
    print("sensor: " + curr_sensor + ", date: " + curr_date + ", sampling: " + fz_select.value)
    get_df()
    df_update_dict = df.to_dict(orient="list")
    df_update_dict[TIME] = list(df.index.values)
    # source.data = {
    #     TIME: df_update.index,
    #     TEMP: df_update[TEMP],
    #     HUM: df_update[HUM],
    #     GAS: df_update[GAS],
    #     PRES: df_update[PRES],
    # }
    source.data = df_update_dict



sensor_select.on_change('value', lambda attr, old, new: update_sensor())
fz_select.on_change('value', lambda attr, old, new: update_fz())
date_select.on_change('value', lambda attr, old, new: update_date())


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
