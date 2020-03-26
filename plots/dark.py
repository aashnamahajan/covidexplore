import os

import pandas as pd
import json
import numpy as np

from bokeh.embed import components
from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, HoverTool, CustomJS, ColumnDataSource, Button, Text
from bokeh.embed import json_item
from bokeh.layouts import widgetbox, row, column
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer, mpl
import geopandas as gpd

from callbacks import get_callback


shapefile = 'data/countries_110m/ne_110m_admin_0_countries.shp'
datafile1 = 'data/cases_per_weeks_bokeh.csv'
datafile2 = 'data/deaths_per_weeks_bokeh.csv'

replacements = {'US':'United States of America',
               'Korea, South':'South Korea',
               'Taiwan*':'Taiwan',
               'Serbia': 'Republic of Serbia'}

gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']

gdf = gdf.drop(gdf.index[159]) # Antarctica
gdf.head()

data1 = pd.read_csv(datafile1)
data2 = pd.read_csv(datafile2)

for c in replacements:
    data1['country'].replace(c, replacements[c], inplace=True)
    data2['country'].replace(c, replacements[c], inplace=True)


def get_cases_plot():
    merged_df = gdf.merge(data1, on='country', how='left')
    merged_df['week'].fillna(-1, inplace=True)

    def json_data(selectedWeek):
        week = selectedWeek
        merged = merged_df[(merged_df['week'] == week) | (merged_df['week'] == -1)]
        print(merged)
        merged_json = json.loads(merged.to_json())
        json_data = json.dumps(merged_json)
        return json_data

    # Input GeoJSON source that contains features for plotting.
    geosource = GeoJSONDataSource(geojson=json_data(4))

    # Define a sequential multi-hue color palette.
    palette = mpl['Magma'][256]
    palette = palette[::-1]

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
    color_mapper = LinearColorMapper(palette=palette, low=0, high=np.max(data1['count'])*0.5, nan_color='#d9d9d9')


    # Add hover tool
    hover = HoverTool(tooltips=[('Country', '@country'), ('cases', '@count')], callback=get_callback('hover_cursor'))

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=20, height=500,
                         border_line_color=None, location=(0, 0), orientation='vertical')

    # Create figure object.
    p = figure(title='Confirmed COVID-19 cases since the 4th week of 2020', plot_height=550, plot_width=1100,
               toolbar_location=None,
               tools=[hover])
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False

    # Add patch renderer to figure.
    p.patches('xs', 'ys', source=geosource, fill_color={'field': 'count', 'transform': color_mapper},
              line_color='black', line_width=0.25, fill_alpha=1)

    p.add_layout(color_bar, 'right')

    Overall = ColumnDataSource(data1)
    Curr = ColumnDataSource(data1[data1['week'] == 4])

    callback = get_callback('dark_slider', [Overall, Curr])

    animate = get_callback('dark_play_button')

    # Make a slider object: slider
    slider = Slider(title='Week', start=4, end=13, step=1, value=4, orientation="horizontal", width=505)
    slider.js_on_change('value', callback)
    callback.args["slider"] = slider
    callback.args["map"] = p

    button = Button(label='► Play', width=505)
    button.js_on_click(animate)
    animate.args['button'] = button
    animate.args['slider'] = slider

    row2 = row(widgetbox(slider), widgetbox(button))
    layout = column(p, row2)
    curdoc().add_root(layout)
    script, div = components(layout)
    return script, div


def get_deaths_plot():
    merged_df = gdf.merge(data2, on='country', how='left')
    merged_df['week'].fillna(-1, inplace=True)

    def json_data(selectedWeek):
        week = selectedWeek
        merged = merged_df[(merged_df['week'] == week) | (merged_df['week'] == -1)]
        print(merged)
        merged_json = json.loads(merged.to_json())
        json_data = json.dumps(merged_json)
        return json_data

    # Input GeoJSON source that contains features for plotting.
    geosource = GeoJSONDataSource(geojson=json_data(4))

    # Define a sequential multi-hue color palette.
    palette = mpl['Magma'][256]
    palette = palette[::-1]

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
    color_mapper = LinearColorMapper(palette=palette, low=0, high=np.max(data2['count'])*0.5, nan_color='#d9d9d9')


    # Add hover tool
    hover = HoverTool(tooltips=[('Country', '@country'), ('cases', '@count')], callback=get_callback('hover_cursor'))

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=20, height=500,
                         border_line_color=None, location=(0, 0), orientation='vertical')

    # Create figure object.
    p = figure(title='Deaths due to COVID-19 since the 4th week of 2020', plot_height=550, plot_width=1100,
               toolbar_location=None,
               tools=[hover])
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False

    # Add patch renderer to figure.
    p.patches('xs', 'ys', source=geosource, fill_color={'field': 'count', 'transform': color_mapper},
              line_color='black', line_width=0.25, fill_alpha=1)

    p.add_layout(color_bar, 'right')

    Overall = ColumnDataSource(data2)
    Curr = ColumnDataSource(data2[data2['week'] == 4])

    callback = get_callback('dark_slider', [Overall, Curr])

    animate = get_callback('dark_play_button')

    # Make a slider object: slider
    slider = Slider(title='Week', start=4, end=13, step=1, value=4, orientation="horizontal", width=505)
    slider.js_on_change('value', callback)
    callback.args["slider"] = slider
    callback.args["map"] = p

    button = Button(label='► Play', width=505)
    button.js_on_click(animate)
    animate.args['button'] = button
    animate.args['slider'] = slider

    row2 = row(widgetbox(slider), widgetbox(button))
    layout = column(p, row2)
    curdoc().add_root(layout)
    script, div = components(layout)
    return script, div