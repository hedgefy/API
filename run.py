#!/usr/bin/env python3

import pandas as pd
import json
import matplotlib
import fbprophet
import os
import requests
import datetime
from flask_restful import reqparse
from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib.parse import urlparse
from flask_classful import FlaskView, route

app = Flask(__name__)
CORS(app)

TOKEN_NAME_TO_ID = {
    'SNX': '2586',
    'BTC': '1',
    'ETH': '1027',
    'YFI': '5864',
    'CRV': '6538',
    'AAVE': '7278',
    'UNI': '7083',
    'sXAU': '6191',
    'sXAG': '5863',
    'iBTC': '6200',
    'iETH': '6188',
}

THETAS = [
    0.01,
    0.1,
    0.5,
    0.9
]

DAYS_TO_FORECAST = 35


def get_actual_epoch() -> int:
    return int(datetime.datetime.now().timestamp())


def get_url(asset_id: int) -> str:
    actual_timestamp = str(get_actual_epoch())
    feb_11_timestamp = str(1518389909)
    url = 'https://web-api.coinmarketcap.com/v1.1/cryptocurrency/quotes/historical?convert=USD&format=chart_crypto_details&id=' + \
        str(asset_id)+'&interval=1d&time_end=' + \
        actual_timestamp+'&time_start='+feb_11_timestamp
    return url


class Hedgefy(FlaskView):
    def __init__(self):
        self.historical_data = {}
        self.plot_ready_prophecy = {}

    @route('/prophet', methods=['GET'])
    def prophet(self):
        self.fetch_historical_data()
        self.gen_prophecy()

        return jsonify({'plot_ready_prophecy': self.plot_ready_prophecy}), 201

    def fetch_historical_data(self):
        for asset_name, asset_id in TOKEN_NAME_TO_ID.items():
            coinmarketcap_api_url = get_url(asset_id)
            print('> Fetching {}'.format(asset_name))
            res = requests.get(coinmarketcap_api_url).json()
            historical_data_from_api: list = res['data']
            temp_dataset = {
                'ds': [],
                'y': []
            }
            for (timestamp, price_obj) in historical_data_from_api.items():
                timestamp = timestamp.split('T')[0]
                temp_dataset['ds'].append(timestamp)
                temp_dataset['y'].append(price_obj['USD'][0])
            self.historical_data[asset_name] = temp_dataset

    def gen_prophecy(self):
        for (asset_name, asset_id) in TOKEN_NAME_TO_ID.items():
            for theta in THETAS:
                dataset = self.historical_data[asset_name]
                df = pd.DataFrame(dataset)
                print('> Generating {} {} prophey'.format(theta, asset_name))
                df_prophet = fbprophet.Prophet(changepoint_prior_scale=theta)
                df_prophet.fit(df)
                df_forecast = df_prophet.make_future_dataframe(
                    periods=int(DAYS_TO_FORECAST))
                df_forecast = df_prophet.predict(df_forecast)
                self.plot_ready_prophecy[asset_name] = {}
                df_forecast.to_json(orient='columns')
                self.plot_ready_prophecy[asset_name]['theta'] = theta
                self.plot_ready_prophecy[asset_name]['prophecy'] = {
                    'ds': df_forecast.ds.tolist(),
                    'y': dataset['y'],
                    'yhat': df_forecast['yhat'].tolist(),
                    'trend': df_forecast['trend'].tolist(),
                    'yhat_upper': df_forecast['yhat_upper'].tolist(),
                    'yhat_lower': df_forecast['yhat_lower'].tolist(),
                }


Hedgefy.register(app, route_base='/')

if __name__ == "__main__":
    # start cron
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
