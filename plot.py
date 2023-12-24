import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import geopandas as gpd
import geoplot
import plotly
import plotly.express as px
import plotly.figure_factory as ff

from analyse import *

LEVEL2_SHAPE_FILE_PATH = './save/gadm41_VNM_shp/gadm41_VNM_2.shp'
LEVEL3_SHAPE_FILE_PATH = './save/gadm41_VNM_shp/gadm41_VNM_3.shp'
labels = {
    'province': 'Tỉnh / Thành phố',
    'district': 'Quận / Huyện / Thị xã',
    'wards': 'Xã / Phường',
    'price': 'Giá',
    'square': 'Diện tích',
    'estate_type': 'Kiểu BĐS',
    'price/square': 'Giá / Diện tích',
    'quantity': 'Số lượng',
    'time': 'Thời gian'
}

def plot_text_count_hist(data, text_columns, labels=None, show_rug=False):
    text_columns = list(text_columns)
    text_lens = [data[text_column].apply(lambda x: len(x.split()) if isinstance(x, str) else 0) for text_column in text_columns]

    fig = ff.create_distplot(text_lens, text_columns, show_rug=show_rug)
    fig.update_layout(
        title='<b>Độ dài của các văn bản tính theo từ</b>',
        xaxis_title='Độ dài',
        yaxis_title='Số lượng',
        labels=labels,
        showlegend=True
    )
    return fig

def plot_mean_price_over_square_in_districts_bar(
        mean_price_over_square_in_districts_df, 
        show_whole_province=False,
        labels=None,
        hover_data=None
):
    if show_whole_province:
        fig = px.bar(data_frame=mean_price_over_square_in_districts_df,
                     x='estate_type', y='price/square', color='estate_type', barmode='group', labels=labels)
        fig.update_layout(xaxis_title='Hà Nội', yaxis_title='Giá trên diện tích')
    else: 
        fig = px.bar(data_frame=mean_price_over_square_in_districts_df,
                     x='district', y='price/square', color='estate_type', barmode='group', labels=labels)
        fig.update_layout(xaxis_title='Quận', yaxis_title='Giá trên diện tích')
    fig.update_layout(margin={"t": 30, "b": 50, "l": 75, "r": 30})
    return fig

def plot_count_estate_type_in_administrative_unit(
        count_estate_type_in_administrative_unit_df,
):
    fig = px.bar(data_frame=count_estate_type_in_administrative_unit_df,
                 barmode='relative',
                 orientation='h',
                 color_continuous_scale='Viridis')
    fig.update_traces(width=0.8)
    fig.update_layout(margin={"t": 30, "b": 50, "l": 75, "r": 30}, width=800, height=600)
    return fig

def plot_scatter(df, x, y, color=None, symbol=None, size=None, hover_data=None, labels=None):
    if not hover_data:
        hover_data = ['province', 'district', 'ward', 'estate_type', 'price/square']
    fig = px.scatter(
        data_frame=df,
        x=x,
        y=y,
        color=color,
        symbol=symbol,
        size=size,
        labels=labels,
        hover_data=hover_data
    )
    fig.update_layout(margin={"t": 30, "b": 50, "l": 75, "r": 30}, width=800, height=600)
    return fig

def plot_histogram(df, x, y=None, range_x=[0, 1e9], color=None, labels=None, yaxis_title='Số lượng'):
    fig = px.histogram(
        data_frame=df,
        x=x,
        y=y,
        range_x=range_x,
        labels=labels,
        color=color
    )
    fig.update_layout(yaxis_title=yaxis_title)
    fig.update_layout(margin={"t": 30, "b": 50, "l": 75, "r": 30}, width=800, height=600)
    return fig

def plot_bar(df, x=None, y=None, color=None, labels=None):
    fig = px.bar(
        data_frame=df,
        x=x,
        y=y,
        labels=labels,
        color=color
    )
    fig.update_layout(margin={"t": 30, "b": 50, "l": 75, "r": 30}, width=800, height=600)
    return fig

def plot_box(df, x, y, boxpoints='all', color=None, hover_data=None, labels=None, box=False, points=False):
    if not hover_data:
        hover_data = ['province', 'district', 'ward', 'estate_type', 'price/square']
    fig = px.box(
        data_frame=df,
        x=x,
        y=y,
        color=color,
        points=points,
        hover_data=hover_data,
        labels=labels,
        # boxpoints=boxpoints
    )
    fig.update_layout(margin={"t": 30, "b": 50, "l": 75, "r": 30}, width=800, height=500)
    return fig

def plot_aggregate_real_estate_in_administrative_unit_with_geo(
        aggregate_real_estate_in_administrative_unit_with_geo_df,
        level,
        color_by,
        labels=None,
        hover_data=None,
):
    if not hover_data:
        hover_data = {}
        for column in aggregate_real_estate_in_administrative_unit_with_geo_df.columns:
            if column != 'geometry':
                hover_data[column] = True
    fig = px.choropleth_mapbox(
        aggregate_real_estate_in_administrative_unit_with_geo_df,
        geojson=aggregate_real_estate_in_administrative_unit_with_geo_df.geometry,
        locations=aggregate_real_estate_in_administrative_unit_with_geo_df.index,
        color=color_by,
        color_continuous_scale='Viridis',
        mapbox_style='carto-positron',
        center={'lat': aggregate_real_estate_in_administrative_unit_with_geo_df.geometry.centroid.y.mean(),
                'lon': aggregate_real_estate_in_administrative_unit_with_geo_df.geometry.centroid.x.mean()},
        zoom=10,
        opacity=0.7,
        labels=labels,
        hover_data=hover_data,
    )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(margin={"t": 0, "b": 0, "l": 0, "r": 0})
    return fig        

def plot_change_value_by_time(line_df, x, y, color, labels=None, markers=True, xaxis_title=None, yaxis_title=None):
    category_orders = {x: np.sort(line_df[x].unique())}
    fig = px.line(
        data_frame=line_df,
        x=x,
        y=y,
        color=color,
        markers=markers,
        category_orders=category_orders,
        labels=labels
    )
    fig.update_layout(margin={"t": 30, "b": 50, "l": 75, "r": 30}, width=800, height=600)
    return fig