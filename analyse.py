import pandas as pd
import numpy as np
import geopandas as gpd
import pyproj

from util import *

def data_to_dataframe(data, median_scale=5):
    df = pd.DataFrame(data)
        
    address_dataframe = pd.DataFrame(df['address'].tolist())
    contact_info_dataframe = pd.DataFrame(df['contact_info'].tolist()).rename(columns={'name': 'contact_name', 'phone': 'contact_phone'})
    extra_infos_dataframe = pd.DataFrame(df['extra_infos'].tolist())

    df = pd.concat([df, address_dataframe, contact_info_dataframe, extra_infos_dataframe], axis=1).drop(columns=['address', 'contact_info', 'extra_infos'])

    df = df[df['district'] != 'None']
    df['post_date'] = pd.to_datetime(df['post_date'], format=r'%Y/%m/%d')
    df['Tầng'] = pd.to_numeric(df['Tầng'], errors='coerce', downcast='integer')
    df['Số phòng ngủ'] = pd.to_numeric(df['Số phòng ngủ'], errors='coerce', downcast='integer')
    df['Số toilet'] = pd.to_numeric(df['Số toilet'], errors='coerce', downcast='integer')
    # df['Số lầu'] = pd.to_numeric(df['Số lầu'], errors='coerce', downcast='integer')
    # df['Lộ giới'] = pd.to_numeric(df['Lộ giới'].str.replace('m', ''), errors='coerce', downcast='float')
    # df['Chiều dài'] = pd.to_numeric(df['Chiều dài'].str.replace('m', ''), errors='coerce', downcast='float')
    # df['Chiều ngang'] = pd.to_numeric(df['Chiều ngang'].str.replace('m', ''), errors='coerce', downcast='float')

    df['price/square'] = df['price']/df['square']
    df.loc[df['price/square'] == np.inf, 'price/square'] = np.nan
    df = df[~df['ward'].isna()]

    df = df[df['price'] < 1e12]
    df = df[df['square'] < 1e4]
    df = df[df['price/square'] < 2e9]
    df = df[df['price/square'] > 2e6]

    median_price_over_square_for_estate = df.groupby(['estate_type', 'province', 'district'])['price/square'].median()
    def compare_to_median(x):
        if x['price/square'] > 5*median_price_over_square_for_estate[x['estate_type']][x['province']][x['district']]:
            return False
        else:
            return True
    keeps = df.apply(axis=1, result_type='expand', func=compare_to_median)
    df = df[keeps == True]
    
    return df

def load_geo_df(shapefile_path):
    name_map = {'NAME_1': 'province',
                'NAME_2': 'district',
                'NAME_3': 'ward',
                'geometry': 'geometry'}
    geo_df = gpd.read_file(shapefile_path)
    columns = ['NAME_1', 'NAME_2', 'NAME_3', 'geometry']
    geo_df.drop(columns=[_ for _ in geo_df.columns.to_list() if not _ in columns], inplace=True)
    columns = geo_df.columns.tolist()
    columns_name_map = {k: name_map[k] for k in columns}
    geo_df.rename(columns=columns_name_map, inplace=True)
    geo_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
    return geo_df

def get_filtered_df(df: pd.DataFrame, columns, desired_values, only_desired_columns=False):
    '''
    columns: list of columns name
    desired_values: list desired values for each column, can be single value or list of values
    '''
    if not isinstance(columns, list):
        columns = [columns]
    if not isinstance(columns, list):
        desired_values = [desired_values]
    assert len(columns) == len(desired_values), 'Number of colummns and lists of desired values are incompatible!'
    
    new_df = df.copy(deep=True)
    for (column, value) in zip(columns, desired_values):
        if isinstance(value, list):
            new_df = new_df[new_df[column].isin(value)]
        else:
            new_df = new_df[new_df[column] == value]
    if only_desired_columns:
        new_df = new_df[columns]
    return new_df

def df_group_by(df: pd.DataFrame, columns, agg_cols='all', agg='mean', reset_index=True):
    '''
    columns: list of columns to perform group by
    agg_cols: list of columns cols to perform aggregate
    agg: ['mean', 'sum', 'count', 'size', 'max']
    '''
    columns = list(columns)
    if agg_cols == 'all':
        agg_cols = df.columns[~df.columns.isin(columns)].to_list()
    else:
        if not isinstance(agg_cols, list):
            agg_cols = [agg_cols]
    new_df = df.copy(deep=True)
    new_df['quantity'] = 1
    pd_groupby_obj = new_df.groupby(columns)
    if agg == 'mean':
        new_df = pd_groupby_obj[agg_cols].mean()
    elif agg == 'sum':
        new_df = pd_groupby_obj[agg_cols].sum()
    elif agg == 'count':
        new_df = pd_groupby_obj[agg_cols].count()
    elif agg == 'size':
        new_df = pd_groupby_obj[agg_cols].size()
    
    if reset_index:
        new_df = new_df.reset_index()
    return new_df

def df_filtered_by_estate_type_and_administrative_unit(df: pd.DataFrame, desired_estate_types, desired_districts, desired_wards):
    filtered_df = df.copy(deep=True)
    if desired_districts:
        filtered_df = get_filtered_df(df=df, columns=['district'],
                                    desired_values=[desired_districts])
    if desired_wards:
        filtered_df = get_filtered_df(df=filtered_df, columns=['ward'],
                                      desired_values=[desired_wards])
    if desired_estate_types:
        filtered_df = get_filtered_df(df=filtered_df, columns=['estate_type'],
                                      desired_values=[desired_estate_types])
    return filtered_df

def df_mean_price_over_square_in_districts(
        level, filtered_df: pd.DataFrame=None, df: pd.DataFrame=None, 
        desired_estate_types=None, desired_districts=None, 
        show_all_types_mean=True):
    '''
    desired_estate_types: list of desired estate types
    desired_districts: list of desired districts
    '''
    assert filtered_df is not None or df is not None, 'None dataframe provided!'
    assert not (show_all_types_mean and df is None), 'Cant show all type mean without full df!'
    if filtered_df is None:
        filtered_df = df_filtered_by_estate_type_and_administrative_unit(df=df,
                                                                        desired_estate_types=desired_estate_types,
                                                                        desired_districts=desired_districts,
                                                                        desired_wards=None)
    if level == 1:
        result_df = df_group_by(df=filtered_df, columns=['estate_type'],
                                agg_cols=['price/square'], agg='mean')
        if show_all_types_mean:
            all_types_mean_df = df_group_by(df=df, columns=['province'],
                                            agg_cols=['price/square'], agg='mean')
            all_types_mean_df['estate_type'] = 'All types'
            result_df = pd.concat([result_df, all_types_mean_df])
    elif level == 2:
        result_df = df_group_by(df=filtered_df, columns=['district', 'estate_type'],
                           agg_cols=['price/square'], agg='mean')
        if show_all_types_mean:
            all_types_mean_df = get_filtered_df(df=df, columns=['district'],
                                                desired_values=[desired_districts])
            all_types_mean_df = df_group_by(df=all_types_mean_df, columns=['district'],
                                            agg_cols=['price/square'], agg='mean')
            all_types_mean_df['estate_type'] = 'All types'
            result_df = pd.concat([result_df, all_types_mean_df])
    return result_df

def df_count_estate_type_in_administrative_unit(
        level, filtered_df:pd.DataFrame=None, df: pd.DataFrame=None,
        desired_estate_types=None, desired_districts=None, desired_wards=None,
        sum_all_estate_type=False
):    
    assert filtered_df is not None or df is not None, 'None dataframe provided!'
    if filtered_df is None:
        filtered_df = df_filtered_by_estate_type_and_administrative_unit(df=df,
                                                                        desired_estate_types=desired_estate_types,
                                                                        desired_districts=desired_districts,
                                                                        desired_wards=desired_wards)
    if sum_all_estate_type:
        if level == 2:
            grouped_df = filtered_df.groupby(['district']).size().fillna(0)
        if level == 3:
            grouped_df = filtered_df.groupby(['ward', 'district']).size().fillna(0)
        result_df = grouped_df.sort_values(ascending=True)
        result_df.name = 'All types'
    else:
        if level == 2:
            grouped_df = filtered_df.groupby(['district', 'estate_type']).size().unstack().fillna(0)
        if level == 3:
            grouped_df = filtered_df.groupby(['district', 'ward', 'estate_type']).size().unstack().fillna(0)
        total_estate_for_units = grouped_df.sum(axis=1)
        sorted_units = total_estate_for_units.sort_values(ascending=True).index
        result_df = grouped_df.loc[sorted_units]
    return result_df

def df_count_administrative_unit_for_estate_type(
        level, filtered_df:pd.DataFrame=None, df: pd.DataFrame=None,
        desired_estate_types=None, desired_districts=None, desired_wards=None,
        sum_all_units=False
):
    assert filtered_df is not None or df is not None, 'None dataframe provided!'
    if filtered_df is None:
        filtered_df = df_filtered_by_estate_type_and_administrative_unit(df=df,
                                                                        desired_estate_types=desired_estate_types,
                                                                        desired_districts=desired_districts,
                                                                        desired_wards=desired_wards)
    
    if sum_all_units:
        grouped_df = filtered_df.groupby(['estate_type']).size().fillna(0)
        result_df = grouped_df.sort_values(ascending=True)
        result_df.name = 'All aministrative units'
    else:
        if level == 2:
            grouped_df = filtered_df.groupby(['estate_type', 'district']).size().unstack().fillna(0)
        if level == 3:
            grouped_df = filtered_df.groupby(['estate_type', 'district', 'ward']).size().unstack().fillna(0)
        total_estate_for_units = grouped_df.sum(axis=1)
        sorted_units = total_estate_for_units.sort_values(ascending=True).index
        result_df = grouped_df.loc[sorted_units]
    return result_df

def df_aggregate_real_estate_in_administrative_unit(
        level, agg_cols, agg, filtered_df:pd.DataFrame=None, df: pd.DataFrame=None,
        desired_estate_types=None, desired_districts=None, desired_wards=None
):
    if not isinstance(agg_cols, list):
        agg_cols = [agg_cols]
    assert filtered_df is not None or df is not None, 'None dataframe provided!'
    if filtered_df is None:
        filtered_df = df_filtered_by_estate_type_and_administrative_unit(df=df,
                                                                        desired_estate_types=desired_estate_types,
                                                                        desired_districts=desired_districts,
                                                                        desired_wards=desired_wards)
    filtered_df['quantity'] = 1

    if level == 1:
        result_df = df_group_by(df=filtered_df, columns=['province'],
                                 agg_cols=agg_cols, agg=agg)
    elif level == 2:
        result_df = df_group_by(df=filtered_df, columns=['province', 'district'],
                                 agg_cols=agg_cols, agg=agg)
    elif level == 3:
        result_df = df_group_by(df=filtered_df, columns=['province', 'district', 'ward'],
                                 agg_cols=agg_cols, agg=agg)
    return result_df

def df_aggregate_real_estate_in_administrative_unit_with_geo(
        level, agg_cols, agg,
        desired_districts, desired_wards,
        geo_df, filtered_df:pd.DataFrame=None, df: pd.DataFrame=None,
        desired_estate_types=None, 
        density=False
):
    '''
    desired_estate_types: list of desired estate types, aggregate over all estate types if None
    desired_districts: list of desired districts, aggregate over all districts if None
    desired_wards: list of desired districts, aggregate over all wards if None
    level: administrative level, {2: district, 3: ward}, this level must match geo_df administrative_level
    agg_cols: ['quantity', 'price', 'square', 'price/square']
    '''

    assert filtered_df is not None or df is not None, 'None dataframe provided!'
    if filtered_df is None:
        filtered_df = df_filtered_by_estate_type_and_administrative_unit(df=df,
                                                                        desired_estate_types=desired_estate_types,
                                                                        desired_districts=desired_districts,
                                                                        desired_wards=desired_wards)
    geo_df = geo_df[geo_df['province'] == 'Hà Nội']
    geo_df = df_filtered_by_estate_type_and_administrative_unit(df=geo_df,
                                                                desired_estate_types=desired_estate_types,
                                                                desired_districts=desired_districts,
                                                                desired_wards=desired_wards)
    grouped_df = df_aggregate_real_estate_in_administrative_unit(
            filtered_df=filtered_df,
            desired_estate_types=desired_estate_types,
            desired_districts=desired_districts,
            desired_wards=desired_wards,
            level=level,
            agg_cols=agg_cols,
            agg=agg
        )
    if level == 2:
        result_df = pd.merge(left=geo_df, right=grouped_df,
                             how='left', on=['province', 'district']).fillna(0)
    elif level == 3:
        result_df = pd.merge(left=geo_df, right=grouped_df,
                             how='left', on=['province', 'district', 'ward']).fillna(0)
    if density:
        for col in agg_cols:
            result_df[col+'_over_area'] = result_df[col] / result_df['geometry'].area
    return result_df

def df_change_value_by_time(
        columns, agg_cols, agg, time_period,
        filtered_df:pd.DataFrame=None, df: pd.DataFrame=None,
        desired_estate_types=None, desired_districts=None, desired_wards=None,
):
    assert time_period in ['Y', 'M', 'D'], 'Invalid time period!'
    if not isinstance(columns, list):
        columns = [columns]
    assert filtered_df is not None or df is not None, 'None dataframe provided!'
    if filtered_df is None:
        filtered_df = df_filtered_by_estate_type_and_administrative_unit(df=df,
                                                                        desired_estate_types=desired_estate_types,
                                                                        desired_districts=desired_districts,
                                                                        desired_wards=desired_wards)
    filtered_df['time'] = filtered_df['post_date'].dt.to_period(time_period).astype(str)
    columns.append('time')
    result_df = df_group_by(df=filtered_df, columns=columns, agg_cols=agg_cols, agg=agg)
    return result_df