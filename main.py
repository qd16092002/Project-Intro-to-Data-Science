import os
import secrets
from draw import *
from util import *
from analyse import *
from plot import *
from PIL import Image
from flask import Flask, render_template,request
import plotly.offline as pyo
from transformers import AutoTokenizer
import plotly.express as px
import plotly.offline as opy
import plotly.graph_objs as go
import torch
import pandas as pd
import io
import base64
from dash import Dash, html, dcc
from modeling import load_pretrained_model
from scaler import Scaler
from inference_api import transform_input, predict_price

from form import InputForm, SelectForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '7d0fb494ff22bc777a2384efae5670f5b6c41fafb4738df9cd4f50741d15dd78'
DEFAULT_PRICE = "0.0 VND"

CONFIG_FILE = "t5config.json"
PRETRAINED_BASE_MODEL_NAME = "VietAI/vit5-base"

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])

def home():
    form = InputForm()
    predicted_price = DEFAULT_PRICE
    if form.validate_on_submit():
        input_encoding = transform_input(tokenizer, form.data)
        price = predict_price(model, scaler, input_encoding)
        predicted_price = f"{price:,}" + " VND"

    return render_template('home.html', title='Home', form=form, predicted_price=predicted_price)

@app.route('/hanoi', methods=['GET', 'POST'])
def hanoi():
    plot_data1=None
    plot_data2=None
    plot_data3=None
    plot_data4=None
    form = SelectForm()
    if form.validate_on_submit():
        desired_estate_types1 = form.data_estate_type1.data
        print("desired_estate_types: ",desired_estate_types1)
        all_figs=province_page(desired_estate_types1)
        plot_data1= all_figs['price_over_square_dist_fig'].to_html(full_html=False)
        plot_data2= all_figs['count_real_estate_fig'].to_html(full_html=False)
        plot_data3= all_figs['mean_price_over_square_fig'].to_html(full_html=False)
        plot_data4= all_figs['geo_map_df_fig'].to_html(full_html=False)

    return render_template(
        'hanoi.html', 
        title='Hanoi', 
        form=form,
        plot_data1=plot_data1,
        plot_data2=plot_data2,
        plot_data3=plot_data3,
        plot_data4=plot_data4,
        )

@app.route('/district', methods=['GET', 'POST'])
def district():
    plot_data1=None
    plot_data2=None
    plot_data3=None
    plot_data4=None
    plot_data5=None
    plot_data6=None
    form = SelectForm()
    if form.validate_on_submit():
        desired_estate_types2 = form.data_estate_type2.data
        desired_districts2 = form.districts.data
        print("desired_estate_types: ",desired_estate_types2)
        print("desired_districts",desired_districts2)
        all_figs=district_page(desired_districts=desired_districts2,desired_estate_types=desired_estate_types2)
        plot_data1 = all_figs['estate_type_count_fig'].to_html(full_html=False)
        plot_data2 = all_figs['scatter_fig'].to_html(full_html=False)
        plot_data3 = all_figs['geo_map_df_fig'].to_html(full_html=False)
        plot_data4 = all_figs['price_over_square_by_time_fig'].to_html(full_html=False)
        plot_data5 = all_figs['price_over_square_fig'].to_html(full_html=False)
        plot_data6 = all_figs['mean_price_over_square_fig'].to_html(full_html=False)

    return render_template(
        'district.html',
        title='District',
        form= form,
        plot_data1=plot_data1,
        plot_data2=plot_data2,
        plot_data3=plot_data3,
        plot_data4=plot_data4,
        plot_data5=plot_data5,
        plot_data6=plot_data6,
        )


if __name__ == '__main__':
    # Khởi tạo mô hình
    use_gpu = False
    device = torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")
    model = load_pretrained_model(CONFIG_FILE,
                                  state_dict_path="checkpoint/model_state_dict2.pt",
                                  device=device)
    
    # Khởi tạo tokenizer
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_BASE_MODEL_NAME)
    
    # Load Scaler
    scaler = Scaler()
    
    app.run(host='0.0.0.0', port=3002, debug=True)
    