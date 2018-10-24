import requests
import unittest
from datetime import datetime
import re


class Testsuit(unittest.TestCase):

    url = 'http://0.0.0.0/ip2w/'

    tag_re = re.compile(r'<[^>]+>')

    weather_parameters = ['Wind', 'Humidity', 'Current temperature',
                          'Atmospheric pressure', 'Conditions']

    def remove_tags(self, text, inserted_separator):
        return self.tag_re.sub(inserted_separator, text)

    def test_request_with_remote_ip(self):
        """Verify that response of request with ip address in url
         returns all expected parameters"""
        raw_response = requests.get(self.url + '41.128.189.53')
        w_conditions = [w.capitalize() for w
                        in self.remove_tags(raw_response.content, ': ').split(': ')]

        for w_param in self.weather_parameters:
            assert w_param in w_conditions

    def test_request_without_ip(self):
        """Verify that response of request without ip address in url
           returns all expected parameters"""
        raw_response = requests.get(self.url)
        w_conditions = [w.capitalize() for w
                        in self.remove_tags(raw_response.content, ': ').split(': ')]

        for w_param in self.weather_parameters:
            assert w_param in w_conditions

    def test_request_spoiled_ip(self):
        """Verify that request with spoiled ip address in url recognized as
        request without ip/with local ip"""
        raw_response1 = requests.get(self.url + 'spoiled')
        raw_response2 = requests.get(self.url)
        w_conditions1 = self.remove_tags(raw_response1.content, '\n').split('\n')
        w_conditions2 = self.remove_tags(raw_response2.content, '\n').split('\n')

        for w_param in w_conditions1:
            try:
                datetime.strptime(w_param, "%Y-%m-%d %H:%M:%S")
                continue
            except ValueError:
                assert w_param in w_conditions2

    def test_response_date(self):
        """Verify that response contains current date"""
        date = datetime.now().strftime("%Y-%m-%d")
        raw_response = requests.get(self.url)
        w_conditions = [w.capitalize() for w
                        in self.remove_tags(raw_response.content, '\n').split('\n')]

        assert date in "\n".join(s for s in w_conditions if date in s).split()


if __name__ == '__main__':
    unittest.main()
