from tests.api_test_base import TestBase
import addresses
import mock

# Set up mock responses for each API that we use to look up postal codes.
ZIPTASTIC_API_RESPONSE = mock.MagicMock(status_code=200)
ZIPTASTIC_API_RESPONSE.json.return_value = {
    "city":  "Brooklyn", "state_short":  "NY"
}

POSTCODES_API_RESPONSE = mock.MagicMock(status_code=200)
POSTCODES_API_RESPONSE.json.return_value = {
    "result": {"admin_district": "North Dorset"}
}

class TestConstuctAddress(TestBase):
    @mock.patch('requests.get', return_value=ZIPTASTIC_API_RESPONSE)
    def test_construct_address_north_america(self, mock_request):
        address = addresses.construct_address(
            '55 Elm Rd',
            'New York City',
            'New York',
            '11216',
            'US'
        )

        # Make sure we made a request to Ziptastic, our source for North
        # American postal codes.
        mock_request.assert_called_once()
        (_, (path,), _) = mock_request.mock_calls[0]
        assert addresses.BASE_ZIPTASTIC_API_URL in path
        # Make sure the address has all the right properties
        assert address.city == 'New York City'
        assert address.postal_code_city == 'Brooklyn' # from API
        assert address.state == 'New York'
        assert address.postal_code_state == 'NY' # from API
        assert address.postal_code == '11216'
        assert address.country == 'us'
        assert address.address == '55 Elm Rd'

    @mock.patch('requests.get', return_value=POSTCODES_API_RESPONSE)
    def test_construct_address_uk(self, mock_request):
        address = addresses.construct_address(
            '55 Elm Rd', 'Somecity', 'Somestate', 'SP7 7BE', 'UK'
        )

        # Make sure we made a request to Postcodes, our source for North
        # American postal codes.
        mock_request.assert_called_once()
        (_, (path,), _) = mock_request.mock_calls[0]
        assert addresses.BASE_POSTCODES_API_URL in path

        # Make sure the address has all the right properties
        assert address.city == 'Somecity'
        assert address.postal_code_city == "North Dorset" # from API
        assert address.state == 'Somestate'
        # Since we don't get a state from UK postal codes, postal_code_state should
        # point to the user-input state.
        assert address.postal_code_state == 'Somestate'
        assert address.postal_code == 'SP7 7BE'
        assert address.country == 'uk'
        assert address.address == '55 Elm Rd'

    @mock.patch('requests.get', return_value=POSTCODES_API_RESPONSE)
    def test_construct_address_london(self, mock_request):
        address = addresses.construct_address(
            '55 Elm Rd', 'London', 'Somestate', 'SP7 7BE', 'UK'
        )

        # Make sure we made a request to Postcodes, our source for North
        # American postal codes.
        mock_request.assert_called_once()
        (_, (path,), _) = mock_request.mock_calls[0]
        assert addresses.BASE_POSTCODES_API_URL in path

        # Make sure the address has all the right properties
        assert address.city == 'London'
        assert address.postal_code_city == "North Dorset" # from API
        assert address.state == 'Somestate'
        # Since we don't get a state from UK postal codes, postal_code_state should
        # point to the user-input state.
        assert address.postal_code_state == 'Somestate'
        assert address.postal_code == 'SP7 7BE'
        assert address.country == 'uk'
        assert address.address == '55 Elm Rd'

class TestGetCityAndStateFromZip(TestBase):
    @mock.patch('requests.get', return_value=ZIPTASTIC_API_RESPONSE)
    def test_get_city_and_state_valid_us_zip(self, mock_request):
        (city, state) = addresses.get_city_and_state_from_postal_code('us', '11216')

        # Make sure we made a request to Ziptastic, our source for North
        # American postal codes.
        mock_request.assert_called_once()
        (_, (path,), _) = mock_request.mock_calls[0]
        assert addresses.BASE_ZIPTASTIC_API_URL in path

        # Check function return value
        assert city == 'Brooklyn'
        assert state == 'NY'

    def test_get_city_and_state_unspported_country(self):
        (city, state) = addresses.get_city_and_state_from_postal_code('gh', '11216')
        assert city == None
        assert state == None
