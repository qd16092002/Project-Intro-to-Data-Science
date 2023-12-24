import json
import string
import sys

import pyproj
import pandas as pd
pd.set_option('display.max_columns', None)  # Show all columns
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import geopandas as gpd
import geoplot
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

from util import *
from analyse import *
from plot import *

data = read_json('./data/bds.json')
df = data_to_dataframe(data=data)
geo_df_level2 = load_geo_df(LEVEL2_SHAPE_FILE_PATH)
geo_df_level3 = load_geo_df(LEVEL3_SHAPE_FILE_PATH)
geo_df = geo_df_level2

def province_page(desired_estate_types):
    filtered_df = df_filtered_by_estate_type_and_administrative_unit(df=df,
                                                                    desired_estate_types=desired_estate_types,
                                                                    desired_districts=None,
                                                                    desired_wards=None)
    # Phân phối giá trên diện tích của các loại BĐS
    price_over_square_dist_df = filtered_df
    price_over_square_dist_fig = plot_histogram(
        df=price_over_square_dist_df,
        x='price/square',
        labels=labels
    )
    # Số lượng BĐS rao bán theo kiểu BĐS
    count_real_estate_df = df_group_by(
        df=df,
        columns=['estate_type'],
        agg_cols=['quantity'],
        agg='count'
    ).sort_values('quantity', ascending=False)
    count_real_estate_fig = plot_bar(
        df=count_real_estate_df,
        x='estate_type',
        y='quantity',
        labels=labels,
        color='estate_type'
    )

    # Giá / diện tích của các loại BĐS
    mean_price_over_square_df = df_mean_price_over_square_in_districts(
        df=df,
        filtered_df=filtered_df,
        desired_estate_types=desired_estate_types,
        level=1,
        show_all_types_mean=True
    )
    mean_price_over_square_fig = plot_mean_price_over_square_in_districts_bar(
        mean_price_over_square_in_districts_df=mean_price_over_square_df,
        labels=labels,
        show_whole_province=True
    )

    # Số lượng BĐS rao bán map
    real_estate_count_geo_df = df_aggregate_real_estate_in_administrative_unit_with_geo(
        filtered_df=filtered_df,
        geo_df=geo_df,
        desired_districts=None,
        desired_wards=None,
        level=2,
        agg_cols='quantity',
        agg='count'
    )
    # Giá trung bình BĐS map
    real_estate_mean_price_over_square_geo_df = df_aggregate_real_estate_in_administrative_unit_with_geo(
        filtered_df=filtered_df,
        geo_df=geo_df,
        desired_districts=None,
        desired_wards=None,
        level=2,
        agg_cols='price/square',
        agg='mean'
    )
    # Kết hợp hai dataframe
    geo_map_df = pd.merge(
        left=real_estate_count_geo_df, right=real_estate_mean_price_over_square_geo_df,
        how='inner'
    )
    geo_map_df_fig = plot_aggregate_real_estate_in_administrative_unit_with_geo(
        aggregate_real_estate_in_administrative_unit_with_geo_df=geo_map_df,
        level=2,
        color_by='quantity',
        labels=labels
    )

    return {
        'price_over_square_dist_fig': price_over_square_dist_fig,
        'count_real_estate_fig': count_real_estate_fig,
        'mean_price_over_square_fig': mean_price_over_square_fig,
        'geo_map_df_fig': geo_map_df_fig
    }

def district_page(desired_districts, desired_estate_types):
    filtered_df = df_filtered_by_estate_type_and_administrative_unit(df=df,
                                                                    desired_estate_types=desired_estate_types,
                                                                    desired_districts=desired_districts,
                                                                    desired_wards=None)
    # Số lượng các kiểu bất động sản
    estate_type_count_df = df_count_estate_type_in_administrative_unit(
        filtered_df=filtered_df,
        level=2
    )
    estate_type_count_fig = plot_count_estate_type_in_administrative_unit(
        count_estate_type_in_administrative_unit_df=estate_type_count_df
    )

    # Scatter plot giá và diện tích
    scatter_df = filtered_df
    scatter_fig = plot_scatter(
        df=scatter_df,
        x='square',
        y='price',
        symbol='estate_type',
        color='district',
        size='price/square',
        labels=labels
    )

    # Phân phối giá trên diện tích
    price_over_square_df = filtered_df
    price_over_square_fig = plot_box(
        df=price_over_square_df,
        x='estate_type',
        y='price/square',
        color='estate_type',
        labels=labels,
        points='outliers'
    )

    # Số lượng BĐS rao bán map
    real_estate_count_geo_df = df_aggregate_real_estate_in_administrative_unit_with_geo(
        filtered_df=filtered_df,
        geo_df=geo_df,
        desired_districts=desired_districts,
        desired_wards=None,
        level=2,
        agg_cols='quantity',
        agg='count'
    )
    # Giá trung bình BĐS map
    real_estate_mean_price_over_square_geo_df = df_aggregate_real_estate_in_administrative_unit_with_geo(
        filtered_df=filtered_df,
        geo_df=geo_df,
        desired_districts=desired_districts,
        desired_wards=None,
        level=2,
        agg_cols='price/square',
        agg='mean'
    )
    # Kết hợp hai dataframe
    geo_map_df = pd.merge(
        left=real_estate_count_geo_df, right=real_estate_mean_price_over_square_geo_df,
        how='inner'
    )
    geo_map_df_fig = plot_aggregate_real_estate_in_administrative_unit_with_geo(
        aggregate_real_estate_in_administrative_unit_with_geo_df=geo_map_df,
        level=2,
        color_by='quantity',
        labels=labels
    )

    # Giá/diện tích trung bình BĐS theo kiểu
    mean_price_over_square_in_districts_df = df_mean_price_over_square_in_districts(
        df=df,
        filtered_df=filtered_df,
        show_all_types_mean=True,
        level=2
    )
    mean_price_over_square_fig = plot_mean_price_over_square_in_districts_bar(
        mean_price_over_square_in_districts_df=mean_price_over_square_in_districts_df,
        labels=labels
    )

    # Giá/diện tích theo thời gian
    price_over_square_by_time_df = df_change_value_by_time(
        filtered_df=filtered_df,
        columns=['district'],
        agg_cols=['price/square'],
        agg='mean',
        time_period='Y'
    )
    price_over_square_by_time_fig = plot_change_value_by_time(
        line_df=price_over_square_by_time_df,
        color='district',
        x='time',   
        y='price/square',
        labels=labels
    )

    return {
        'estate_type_count_fig': estate_type_count_fig,# Số lượng các kiểu bất động sản
        'scatter_fig': scatter_fig, # Scatter plot giá và diện tích
        'geo_map_df_fig': geo_map_df_fig, # Kết hợp hai dataframe
        'price_over_square_by_time_fig': price_over_square_by_time_fig, # Giá/diện tích theo thời gian
        'price_over_square_fig': price_over_square_fig, # Phân phối giá trên diện tích
        'mean_price_over_square_fig': mean_price_over_square_fig # Giá/diện tích trung bình BĐS theo kiểu
    }
    
    
    
    