# uWSGI_weather
Python version: 2.7.12

simple uWSGI daemon for CentOS 7 for weather determination by ip

Way to install:
```
rpm -ivh rpmbuild/RPMS/noarch/ip2w-0.0.1-1.noarch.rpm
```
To build rpm from sources:
```
yum -y install rpmdevtools*
rpmdev-setuptree
rpmbuild -ba --clean ip2w.spec
```
*in case of try to adapt source code for debian platform replace user:nginx patterns with 
user:www-data in uwsgi_weather.service. Same will be in your nginx.conf file

Running:
```
service uwsgi_weather start
```
Using:
```
curl http://0.0.0.0/ip2w/41.128.189.53
```
Expected returned value - simple html page with data about weather in area determined 
by given ip address or local weather if ip is not specified:
```
<p>Wind: 3.1 m/sec</p>
<p>Humidity: 36%</p>
<p>current temperature: 27.0 &deg;C</p>
<p>2018-10-24 01:00:00</p>
<p>atmospheric pressure: 757.562191604 millimeters of mercury</p>
<p>Conditions: overcast clouds</p>
```

Running of tests (requires having running uwsgi service):
```
python -m unittest uwsgi_weather_tests
```
