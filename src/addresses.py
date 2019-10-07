"""
A "postal code" (called a "zip code" in the US) is a string of letters/numbers
associated with a particular geographic region. The postal code can be used to
look up geographic information such as city or state/province.

For reporting purposes, we want to record an accurate state for each payment
card entered by our users. (We want to be able to answer questions like,
"How many dollars did users with New York payment cards transfer in 2018?")
We can't trust the user-entered state; users can enter any state they want and
we have no way to verify the accuracy of the data. But we CAN trust the
postal code, since we use an external service to verify that users enter the
correct postal codes for their payment cards. Using external APIs, we can
look up the the state and city associated with this postal code and save it
with the payment card's address.

This module exposes a function `construct_address` which takes various pieces
of address-related data and returns an instance of the Address class, with
the data standardized and with the columns postal_code_city and
postal_code_state populated if possible.
"""

# python
import re
from typing import Optional, Tuple, Dict

# this package
from configvars import config
from models import Address

# deps
import requests

BASE_ZIPTASTIC_API_URL = 'http://zip.getziptastic.com/v2/'
BASE_POSTCODES_API_URL = 'http://api.postcodes.io/postcodes/'

def construct_address(
    street_address: str,
    city: str,
    state: str,
    postal_code: str,
    country: str
) -> Address:
    """Constructs an Address instance with properly formatted fields and, if
    applicable:
        * `postal_code_city`: the city inferred from the zip code
        * `postal_code_state`: the state inferred from the zip code
    """
    (postal_code_city, postal_code_state
        ) = get_city_and_state_from_postal_code(country, postal_code)
    return Address(
        address = street_address,
        city = city,
        state = state,
        postal_code = postal_code,
        postal_code_city = postal_code_city,
        postal_code_state = postal_code_state,
        country=country.lower()
    )

def get_api_headers(api_name: str) -> Dict:
    if api_name == 'ziptastic':
        return { "x-key" : config.ZIPTASTIC_API_KEY }
    if api_name == 'postcodes':
        return {}
    return {}

def get_city_and_state_from_postal_code(
    country_name: str, # the two letter code for the country
    postal_code: str
) -> Tuple[Optional[str], Optional[str]]:
    """ Given a country code and a zip, fetch the city and state."""
    standardized_country_code = country_name.upper()
    if standardized_country_code == 'GB' or standardized_country_code == 'UK':
        resp = requests.get(
            BASE_POSTCODES_API_URL+postal_code,
            headers = get_api_headers('postcodes')
        )
        rjson = resp.json()
        result = rjson.get('result', {})
        city = result['admin_district'] if 'admin_district' in result else None
        return (city, None)
    elif (
        standardized_country_code == 'US'
        or standardized_country_code == 'CA'
        or standardized_country_code == 'fr'
    ):
        # FYI: Other countries Ziptastic supports:
        # https://www.getziptastic.com/faq
        try:
            resp = requests.get(
                f'{BASE_ZIPTASTIC_API_URL}{standardized_country_code}/{postal_code}',
                headers = get_api_headers('ziptastic')
            )
            rjson = resp.json()
        except:
            return (None, None)

        city = rjson.get('city', '')
        state = rjson['state_short'] if 'state_short' in rjson else None

        return (city, state)
    else:
        return (None, None)
