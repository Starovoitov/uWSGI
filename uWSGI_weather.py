# -*- coding: utf-8 -*-
import urllib
import urllib2
import logging
import json
import re


def api_get_request(url, args, log):
    """returns response of GET request to url and pass args as parameters"""
    get_params = urllib.urlencode(args)
    req = urllib2.Request(url + '?' + get_params)
    log.debug(req.get_full_url() + ' - full request to service')
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
    """returns atmospheric pressure (mm of mercury)"""
    def hpa_to_mm_mercury(hpa_val):
        """convert 10^2 Pascals to millimeters of mercury"""
        return hpa_val * 100.0 / 133.322387415

    return 'atmospheric pressure: ' + str(hpa_to_mm_mercury(api_data['main']['pressure'])) + ' millimeters of mercury'


def response_get_temperature(api_data):
    """returns temperature (Celsius)"""
    def k_to_celsium(k_val):
        """coverts Kelvin degrees to Celsius"""
        return k_val - 273.15

    return 'current temperature: ' + str(k_to_celsium(api_data['main']['temp'])) + ' &deg;' + 'C'


def response_get_humidity(api_data):
    """returns relative humidity"""
    return 'Humidity: ' + str(api_data['main']['humidity']) + '%'


def response_get_wind(api_data):
    """returns wind speed (m/s)"""
    return 'Wind: ' + str(api_data['wind']['speed']) + ' m/sec'


def response_get_conditions(api_data):
    """returns verbal description of weather"""
    return "Conditions: " + str(api_data['weather'].pop()['description'])


def build_response(api_data):
    """returns html page with response from weather api"""
    response = []

    for i in globals():
        item = globals()[i]
        if callable(item) and "response_get" in i:
            response.append('<p>' + item(api_data) + '</p>')
    return response


def read_conf(opts, conf):
    """read conf file and initialize opts settings"""
    settings = []

    try:
        config_file = open(conf, 'r')
        if config_file.mode == 'r':
            settings = config_file.read().split("\n")
        config_file.close()
    except IOError or EOFError:
        return False

    for line in settings:
        if not line.lstrip().startswith('#') and line is not "":
            file_opt = line.split("=")
            if opts[file_opt[0]]:
                opts[file_opt[0]] = file_opt[1]
    return True


def application(environ, start_response):

    opts = {
        "config": "/usr/local/etc/uwsgi.conf",
        "log_level": "INFO",
        "log_path": "/var/log/uwsgi_weather.log",
        "token": "6d867ad27aea75",
        "appid": "972c2264ea91f1f814dbe62f5208c9e1",
        "location_determination": "https://ipinfo.io",
        "weather_determination": "https://api.openweathermap.org/data/2.5/weather"
    }

    conf_status = read_conf(opts, opts["config"])

    logging.basicConfig(filename=opts["log_path"],
                        level=logging.getLevelName(opts['log_level']),
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')

    if not conf_status:
        logging.critical("config file is not file or corrupted - default values in use")

    # authorization tokens, taken from credentials given by api
    ipinfo_args = {'token': opts['token']}
    openweather_args = {'appid': opts['appid']}

    # api urls
    location_determination = opts['location_determination']
    weather_determination = opts['weather_determination']

    try:
        ip = re.search('(?<=ip2w/)[0-9]+(?:\.[0-9]+){3}', environ['PATH_INFO'])
        if ip:
            location_determination += ('/' + ip.group(0))
            logging.info("ip address for location of weather is found")
        else:
            logging.info("No ip address is given - weather determination "
                         "will use ip address of wsgi service")

        start_response('200 OK', [('Content-Type', 'text/html')])

        lat, lon = api_get_request(location_determination, ipinfo_args, logging)['loc'].split(',')
        logging.info("connection to location determination - " +
                     location_determination + " is successful")

        openweather_args['lat'] = lat
        openweather_args['lon'] = lon
        data = api_get_request(weather_determination, openweather_args, logging)
        logging.info("connection to weather determination - " +
                     weather_determination + " is successful")

        return build_response(data)
    except urllib2.URLError:
        logging.critical("Connection to weather api failed")
        return ["<h3 style='color:red'>Connection to weather api failed</h3>"]
