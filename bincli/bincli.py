#! /usr/bin/env python3

import hashlib, hmac, time, requests, sys

class BinanceClient:
    def __init__(self, key, secret, maxtx=1000, debug=False):
        self.api_key = key
        self.api_secret = secret
        self.in_run = False
        self.balance = None
        self.debug = debug
        self.maxtx = maxtx

    def get_signature(self, params):
        return hmac.new(self.api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()

    def get_time(self):
        return int(round(time.time() * 1000))

    def http_client(self, req_type, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'Content-Type': 'application/json',
            'X-MBX-APIKEY': self.api_key
        }
        try:
            if req_type == 'del':
                return requests.delete(url, headers=headers, timeout=30).json()
            elif req_type == 'post':
                return requests.post(url, headers=headers, timeout=30).json()
            else:
                return requests.get(url, headers=headers, timeout=30).json()
        except Exception as e:
            if self.debug:
                print(e, file=sys.stderr)
            pass

    def get_price(self, symbol):
        payload = f'symbol={symbol}&timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/ticker/price?{payload}&signature={signature}'
        data = self.http_client('get', url)
        return float(data['price'])

    def exchange_info(self):
        payload = f'timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/exchangeInfo?{payload}&signature={signature}'
        data = self.http_client('get', url)
        return data

    def get_balance(self):
        payload = f'timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v2/balance?{payload}&signature={signature}'
        data = self.http_client('get', url)
        balance = [x['balance'] for x in data if int(float(x['balance'])) != 0]
        self.balance = float(balance[0])

    def get_kline_data(self, symbol, tf):
        payload = f'symbol={symbol}&interval={tf}&limit=1500&timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/klines?{payload}&signature={signature}'
        data = self.http_client('get', url)
        return data

    def base_precision(self, symbol):
        data = self.exchange_info()
        item = [item for item in data['symbols'] if item['symbol'] == symbol][0]
        return item

    def leverage_info(self, symbol):
        payload = f'symbol={symbol}&timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/leverageBracket?{payload}&signature={signature}'
        data = self.http_client('get', url)
        return data

    def positions_info(self):
        payload = f'timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v2/positionRisk?{payload}&signature={signature}'
        data = self.http_client('get', url)
        open_positions = []
        for x in data:
            if float(x['positionAmt'].replace('-', '')) > 0.00:
                s = x['symbol']
                e = float(x['entryPrice'])
                q = float(x['positionAmt'].replace('-', ''))
                p = x['positionSide']
                open_positions.append({'symbol': s, 'entryPrice': e,'quantity': q, 'positionSide': p})
        return open_positions

    def set_leverage(self, symbol, leverage):
        payload = f'symbol={symbol}&leverage={leverage}&timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/leverage?{payload}&signature={signature}'
        data = self.http_client('post', url)
        return data

    def hedge_mode(self, mode):
        payload = f'dualSidePosition={mode}&timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/positionSide/dual?{payload}&signature={signature}'
        data = self.http_client('post', url)
        return data

    def create_order(self, symbol, side, quantity, signal):
        payload = f'symbol={symbol}&type=MARKET&side={side}&quantity={quantity}&positionSide={signal}&timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/order?{payload}&signature={signature}'
        data = self.http_client('post', url)
        if self.debug:
            print(data, file=sys.stderr)

    def tp_sl_order(self, symbol, order, side, signal, price):
        payload = f'symbol={symbol}&type={order}&side={side}&positionSide={signal}&stopPrice={price}&closePosition=true&timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/order?{payload}&signature={signature}'
        data = self.http_client('post', url)
        if self.debug:
            print(data, file=sys.stderr)

    def close_all_orders(self, symbol):
        payload = f'symbol={symbol}&timestamp={self.get_time()}'
        signature = self.get_signature(payload)
        url = f'https://fapi.binance.com/fapi/v1/allOpenOrders?{payload}&signature={signature}'
        data = self.http_client('del', url)
        if self.debug:
            print(data, file=sys.stderr)

    def entry_tpsl(self, symbol, margin, leverage, signal, tp, sl):
        if '%' in margin:
            self.get_balance()
            margin = ((self.balance * int(margin.replace('%', ''))) / 100)
        base_precision = self.base_precision(symbol)
        price = self.get_price(symbol)
        quantity = f"{float(margin) * leverage / float(price):.{base_precision['quantityPrecision']}f}"
        if signal == 'long':
            self.create_order(symbol, 'BUY', quantity, 'LONG')
            tp_price = f"{price + (price * tp):.{base_precision['pricePrecision']}f}"
            sl_price = f"{price - (price * sl):.{base_precision['pricePrecision']}f}"
            self.tp_sl_order(symbol, 'TAKE_PROFIT_MARKET', 'SELL', 'LONG', tp_price)
            self.tp_sl_order(symbol, 'STOP_MARKET', 'SELL', 'LONG', sl_price)
        elif signal == 'short':
            self.create_order(symbol, 'SELL', quantity, 'SHORT')
            tp_price = f"{price - (price * tp):.{base_precision['pricePrecision']}f}"
            sl_price = f"{price + (price * sl):.{base_precision['pricePrecision']}f}"
            self.tp_sl_order(symbol, 'TAKE_PROFIT_MARKET', 'BUY', 'SHORT', tp_price)
            self.tp_sl_order(symbol, 'STOP_MARKET', 'BUY', 'SHORT', sl_price)
        print(f"{signal.upper()} {symbol} @ {price}", file=sys.stderr)

    def entry_market(self, symbol, margin, leverage, signal):
        if '%' in margin:
            self.get_balance()
            margin = ((self.balance * int(margin.replace('%', ''))) / 100)
        base_precision = self.base_precision(symbol)
        price = self.get_price(symbol)
        quantity = f"{float(margin) * leverage / float(price):.{base_precision['quantityPrecision']}f}"
        if signal == 'long':
            self.create_order(symbol, 'BUY', quantity, 'LONG')
        elif signal == 'short':
            self.create_order(symbol, 'SELL', quantity, 'SHORT')
        print(f"{signal.upper()} {symbol} @ {price}", file=sys.stderr)

    def exit_market(self, symbol, position_info):
        for item in position_info:
            if item['symbol'] == symbol:
                if item['positionSide'] == 'LONG':
                    price = self.get_price(symbol)
                    self.create_order(item['symbol'], 'SELL', item['quantity'], 'LONG')
                    if price > item['entryPrice']:
                        print(f"TP {symbol} @ {price}", file=sys.stderr)
                    else:
                        print(f"SL {symbol} @ {price}", file=sys.stderr)
                elif item['positionSide'] == 'SHORT':
                    price = self.get_price(symbol)
                    self.create_order(item['symbol'], 'BUY', item['quantity'], 'SHORT')
                    if price < item['entryPrice']:
                        print(f"TP {symbol} @ {price}", file=sys.stderr)
                    else:
                        print(f"SL {symbol} @ {price}", file=sys.stderr)

    def run(self, symbol, leverage, margin, signal):
        while self.in_run:
            time.sleep(0.5)
        self.in_run = True
        position_info = self.positions_info()
        if self.debug:
            print(position_info, file=sys.stderr)
        if signal == 'flat':
            if position_info:
                try:
                    self.exit_market(symbol, position_info)
                except Exception as e:
                    if self.debug:
                        print(e, file=sys.stderr)
                    pass
        else:
            if len(position_info) < self.maxtx:
                try:
                    self.entry_market(symbol, str(margin), leverage, signal)
                except Exception as e:
                    if self.debug:
                        print(e, file=sys.stderr)
                    pass
        self.in_run = False
        return None

    def tpsl_run(self, symbol, leverage, margin, signal, tp, sl):
        while self.in_run:
            time.sleep(0.5)
        self.in_run = True
        try:
            self.close_all_orders(symbol)
            self.exit_market(symbol)
            self.entry_tpsl(symbol, str(margin), leverage, signal, tp, sl)
        except Exception as e:
            if self.debug:
                print(e, file=sys.stderr)
            pass
        self.in_run = False
        return None
