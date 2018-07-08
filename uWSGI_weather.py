# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import io


# authorization tokens, taken from credentials given by api
ipinfo_args = {'token': '6d867ad27aea75'}
openweather_args = {'appid': '972c2264ea91f1f814dbe62f5208c9e1'}

# api urls
location_determination = 'https://ipinfo.io'
weather_determination = 'https://api.openweathermap.org/data/2.5/weather'

# folder of http server where received data are stored
server_root_folder = '/var/www/html/weather'


def api_get_request(url, args):
    """returns response of GET request to url and pass args as parameters"""
    get_params = urllib.urlencode(args)
    req = urllib2.Request(url + '?' + get_params)

    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'curl/7.37.0')]
    response = opener.open(req)
    return json.loads(response.read())


def response_get_date(api_data):
    """returns formatted date of latest data"""
    import datetime
    return datetime.datetime.fromtimestamp(int(api_data['dt'])).strftime('%Y-%m-%d %H:%M:%S')


def response_get_location(api_data):
    """returns location of request - city, country code and pair latitude/longitude"""
    return api_data['name'] + ', ' + api_data['sys']['country'] + '\r\nCoords: ' + json.dumps(api_data['coord'])


def response_get_pressure(api_data):
    """returns atmospheric pressure"""
    def hpa_to_mm_mercury(hpa_val):
        """convert 10^2 Pascals to millimeters of mercury"""
        return hpa_val * 100.0 / 133.322387415

    return 'atmospheric pressure: ' + str(hpa_to_mm_mercury(api_data['main']['pressure'])) + ' millimeters of mercury'


def response_get_temperature(api_data):
    """returns temperature"""
    def k_to_celsium(k_val):
        """coverts Kelvin degrees to Celsius"""
        return k_val - 273.15

    return 'current temperature: ' + str(k_to_celsium(api_data['main']['temp'])) + ' &deg;' + 'C'


def response_get_humidity(api_data):
    """returns relative humidity"""
    return 'Humidity: ' + str(api_data['main']['humidity']) + '%'


def response_get_wind(api_data):
    """returns wind speed"""
    return 'Wind: ' + str(api_data['wind']['speed']) + ' m/sec'


def dump_to_file(api_data, filename):
    """calls all function containing 'response_get' in
    signature and writes output into http server root folder"""
    try:
        fd = io.open(filename + "/index.html", "w+", encoding='utf-8')
        fd.write(unicode('<html>\r\n<body>\r\n'))
        for i in globals():
            item = globals()[i]
            if callable(item) and "response_get" in i:
                fd.write(unicode('<p>' + item(api_data) + '</p>'))
        fd.write(unicode('</body>\r\n</html>\r\n'))
        fd.close()
    except IOError:
        pass


try:
    lat, lon = api_get_request(location_determination, ipinfo_args)['loc'].split(',')
    openweather_args['lat'] = lat
    openweather_args['lon'] = lon

    data = api_get_request(weather_determination, openweather_args)

    dump_to_file(data, server_root_folder)

except urllib2.URLError:
    pass
except KeyboardInterrupt:
    pass
