import requests
import json
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)

class SensibullQuotes:
    def __init__(self):
        self.base_url = 'https://oxide.sensibull.com/v1/compute'
        self.derivatives_url = f'{self.base_url}/cache/instrument_metacache/2'
        self.live_prices_url = f'{self.base_url}/cache/live_derivative_prices'
        self.quotes_url = f'{self.base_url}/cache/quotes_v2'
        self.derivatives_data = None
        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': 'SensibullQuotes/1.0.0'
        }
        self.cookies = {}

    def fetch_derivatives_data(self, max_retries=3):
        for attempt in range(max_retries):
            try:
                response = requests.get(self.derivatives_url, cookies=self.cookies, headers=self.headers)
                response.raise_for_status()
                self.derivatives_data = response.json()
                logger.info("Successfully fetched derivatives data")
                return
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed to fetch derivatives data: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        logger.error("Failed to fetch derivatives data after maximum retries")

    def get_tradingsymbol(self, instrument_token):
        if not self.derivatives_data:
            self.fetch_derivatives_data()
        
        if self.derivatives_data:
            for symbol, data in self.derivatives_data['derivatives'].items():
                for expiry, expiry_data in data['derivatives'].items():
                    if 'FUT' in expiry_data and expiry_data['FUT']['instrument_token'] == instrument_token:
                        return expiry_data['FUT']['tradingsymbol']
                    if 'options' in expiry_data:
                        for strike, strike_data in expiry_data['options'].items():
                            for option_type in ['CE', 'PE']:
                                if option_type in strike_data and strike_data[option_type]['instrument_token'] == instrument_token:
                                    return strike_data[option_type]['tradingsymbol']
            logger.warning(f"No trading symbol found for instrument token: {instrument_token}")
        else:
            logger.error("Failed to get trading symbol: Derivatives data not available")
        return None

    def get_live_derivative_prices(self, instrument_token):
        if not self.derivatives_data:
            self.fetch_derivatives_data()
        
        if not self.derivatives_data:
            logger.error("Cannot get live derivative prices: Derivatives data not available")
            return None

        url = f"{self.live_prices_url}/{instrument_token}"
        
        try:
            response = requests.get(url, cookies=self.cookies, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if data['status']:
                return self._process_live_derivative_data(data['data'])
            else:
                logger.error("Failed to get live derivative prices: API returned unsuccessful status")
        except requests.RequestException as e:
            logger.error(f"Failed to get live derivative prices: {str(e)}")
        return None

    def _process_live_derivative_data(self, data):
        processed_data = {
            'underlying_token': data['underlying_token'],
            'underlying_price': data['underlying_price'],
            'last_updated_at': data['last_updated_at'],
            'expiries': []
        }

        sorted_expiries = sorted(data['per_expiry_data'].items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))

        for expiry, expiry_data in sorted_expiries:
            processed_expiry = {
                'expiry': expiry,
                'atm_strike': expiry_data['atm_strike'],
                'atm_iv': expiry_data['atm_iv'],
                'future_price': expiry_data['future_price'],
                'max_oi': expiry_data['max_oi'],
                'options': []
            }

            sorted_options = sorted(expiry_data['options'], key=lambda x: x['token'])
            atm_index = next((i for i, opt in enumerate(sorted_options) if opt['token'] > expiry_data['atm_strike']), len(sorted_options)//2)
            start_index = max(0, atm_index - 10)
            end_index = min(len(sorted_options), atm_index + 10)
            selected_options = sorted_options[start_index:end_index]

            for option in selected_options:
                if option['greeks_with_iv']:
                    processed_option = {
                        'token': option['token'],
                        'tradingsymbol': self.get_tradingsymbol(option['token']),
                        'last_price': option['last_price'],
                        'oi': option['oi'],
                        'volume': option['volume'],
                        'is_liquid': option['is_liquid'],
                        'delta': option['greeks_with_iv']['delta'],
                        'theta': option['greeks_with_iv']['theta'],
                        'gamma': option['greeks_with_iv']['gamma'],
                        'vega': option['greeks_with_iv']['vega'],
                        'iv': option['greeks_with_iv']['iv']
                    }
                    processed_expiry['options'].append(processed_option)
            
            processed_data['expiries'].append(processed_expiry)

        return processed_data

    def get_quotes(self, trading_symbols):
        if isinstance(trading_symbols, str):
            trading_symbols = [trading_symbols]
        
        json_data = {
            'trading_symbols': trading_symbols,
        }
        
        try:
            response = requests.post(self.quotes_url, cookies=self.cookies, headers=self.headers, json=json_data)
            response.raise_for_status()
            data = response.json()
            if data['success']:
                return {symbol: self._extract_quote_info(quote_data) 
                        for symbol, quote_data in data['payload'].items()}
            else:
                logger.error("Failed to get quotes: API returned unsuccessful status")
        except requests.RequestException as e:
            logger.error(f"Failed to get quotes: {str(e)}")
        return None

    def _extract_quote_info(self, quote_data):
        return {
            'last_price': quote_data.get('last_price'),
            'instrument_token': quote_data.get('instrument_token'),
            'underlying_instrument': quote_data.get('underlying_instrument'),
            'tradingsymbol': quote_data.get('tradingsymbol'),
            'segment': quote_data.get('segment'),
            'exchange': quote_data.get('exchange'),
            'instrument_type': quote_data.get('instrument_type'),
            'last_updated_at': quote_data.get('last_updated_at'),
            'strike': quote_data.get('strike'),
            'expiry': quote_data.get('expiry'),
            'oi': quote_data.get('oi'),
            'volume': quote_data.get('volume')
        }
