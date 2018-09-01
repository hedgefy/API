if __name__ == '__main__':
    from termcolor import cprint
    import sys
    if len(sys.argv) != 2:
        print('\n')
        cprint('> Usage: python3 run.py [PORT]', 'cyan')
        print('\n')
        exit()
    port = int(sys.argv[1])    
    cprint('     .___             .__       .__    .__             .__         ', 'cyan')
    cprint('   __| _/___________  |__| ____ |  |__ |__| ____  ____ |__| ____   ', 'cyan')
    cprint('  / __ |\_  __ \__  \ |  |/ ___\|  |  \|  |/ ___\/  _ \|  |/    \  ', 'cyan')
    cprint(' / /_/ | |  | \// __ \|  \  \___|   Y  \  \  \__(  <_> )  |   |  \ ', 'cyan')
    cprint(' \____ | |__|  (____  /__|\___  >___|  /__|\___  >____/|__|___|  / ', 'cyan')
    cprint('      \/            \/        \/     \/        \/              \/  ', 'cyan')
    cprint('                             {}'.format(port), 'magenta')

    import pandas as pd
    import hashlib, json, requests, fbprophet
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse

    app = Flask(__name__)
    CORS(app)

    @app.route('/prophet', methods=['POST'])
    def prophet():
        values = request.get_json()
        ds = values.get('ds')
        y = values.get('y')
        df = pd.DataFrame(values)
        #------------------------------------------------------------->
        df_prophet = fbprophet.Prophet(changepoint_prior_scale=0.05)
        df_prophet.fit(df)
        #------------------------------------------------------------->
        df_forecast = df_prophet.make_future_dataframe(periods=int(1))
        df_forecast = df_prophet.predict(df_forecast)
        df_forecast.to_json(orient='columns')
        # print(df_forecast.keys())
        if ds is None:
            return "Error: routes.py:17, ds is None", 400
        return jsonify({
            'ds': ds,
            'y': y,
            'yhat': df_forecast['yhat'].tolist(),
            'trend': df_forecast['trend'].tolist(),
            'yhat_upper': df_forecast['yhat_upper'].tolist(),
            'yhat_lower': df_forecast['yhat_lower'].tolist()
        }), 201

    app.run(host='127.0.0.1', port=port)
