import pandas as pd
import json
import matplotlib
import fbprophet
import os
import requests
from flask_restful import reqparse
from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib.parse import urlparse
from flask_classful import FlaskView, route

app = Flask(__name__)
CORS(app)

TOKEN_NAME_TO_ID = {
    'sXAU': '6191',
    'iBTC': '6200',
    'BTC': '1',
    'BNB': '1839',
    'ETH': '1027',
    'iETH': '6188',
}


class Hedgefy(FlaskView):
    def __init__(self):
        self.thetas = [0.1, 0.5, 0.75, 1.0]
        self.historical_data = {}
        self.plot_ready_prophecy = {}

    @route('/prophet', methods=['POST'])
    def prophet(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('assets', type=list)
        parser.add_argument('currency', type=str)
        parser.add_argument('theta', type=float)
        parser.add_argument('data-length', type=str)
        parser.add_argument('forecast-days', type=str)
        args = parser.parse_args()
        res = requests.get(
            'https://web-api.coinmarketcap.com/v1.1/cryptocurrency/quotes/historical?convert=USD&format=chart_crypto_details&id=6191&interval=1d&time_end=1612407600&time_start=1597017600')
        return res.json(), 201
        for asset in args.asset:
            self.fetch_historical_data_for(asset)
            for theta in self.thetas:
                self.gen_prophecy_for(asset, theta)
        data = self.plot_ready_prophecy
        return jsonify({'data': data}), 201

    def fetch_historical_data_for(self, asset: str):
        res = requests.get(
            'https://web-api.coinmarketcap.com/v1.1/cryptocurrency/quotes/historical?convert=USD,BTC&format=chart_crypto_details&id=6191&interval=1d&time_end=1612407600&time_start=1597017600')

        self.historical_data[asset] = []

    def gen_prophecy_for(self, asset: str, theta: float):
        self.plot_ready_prophecy = {}
        # ! refactor
        # df = pd.DataFrame(dataset)
        # # ------------------------------------------------------------->
        # df_prophet = fbprophet.Prophet(
        #     changepoint_prior_scale=changepoint_prior_scale)
        # df_prophet.fit(df)
        # # ------------------------------------------------------------->
        # df_forecast = df_prophet.make_future_dataframe(periods=int(forecast_days))
        # df_forecast = df_prophet.predict(df_forecast)
        # df_forecast.to_json(orient='columns')
        # # print(df_forecast.keys())
        # if ds is None:
        #     return "Error: routes.py:17, ds is None", 400
        # return jsonify({
        #     'ds': df_forecast.ds.tolist(),
        #     'y': y,
        #     'yhat': df_forecast['yhat'].tolist(),
        #     'trend': df_forecast['trend'].tolist(),
        #     'yhat_upper': df_forecast['yhat_upper'].tolist(),
        #     'yhat_lower': df_forecast['yhat_lower'].tolist()
        # }), 201


Hedgefy.register(app, route_base='/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
