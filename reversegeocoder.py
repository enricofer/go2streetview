import urllib
import urllib2
import simplejson

class ReverseGeocoder(object):
    def __init__(self, base_url = "http://open.mapquestapi.com/nominatim/v1/reverse?format=json"):
        self.base_url = base_url + "&%s"

    def geocode(self, lat, lon, zoom = 18):
        
        params = { 'lat' : lat , 'lon' : lon , 'zoom' : zoom}

        url = self.base_url % urllib.urlencode(params)
        data = urllib2.urlopen(url)
        response = data.read()
        parsedResponse = self.parse_json(response)
        print parsedResponse
        result = "geocode error"
        if 'full_address' in parsedResponse:
            result = parsedResponse['full_address']
        return result

    def parse_json(self, data):
        try:
            jsondata = simplejson.loads(data)

            if "error" in data:
              jsondata['full_address'] = jsondata['error']
            elif "display_name" in data:
              jsondata['full_address'] = jsondata['display_name']
            else:
              jsondata['full_address'] = "Unknown"

        except simplejson.JSONDecodeError:
            jsondata = []
        
        return jsondata