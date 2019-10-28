import requests
import json
import sys, traceback
from keys import ashrae_tmy_key
from reo.log_levels import log


class DeveloperREOapi:

    def __init__(self,
                 lat, lon,
                 url_base="https://developer.nrel.gov/api/reo/v3.json",
                 api_key=ashrae_tmy_key,
                 search_radius=25,
                 output_fields="ashrae_tmy",
                 ):
        self.lat = lat
        self.lon = lon
        self.url_base = url_base
        self.api_key = api_key
        self.search_radius = search_radius
        self.output_fields = output_fields
        self.called_api = False

    @property
    def url(self):
        url = self.url_base + "?api_key=" + self.api_key + "&lat=" + str(self.lat) + "&lon=" + str(self.lon) \
              + "&distance=" + str(self.search_radius) + "&output_fields=" + self.output_fields
        return url

    def get_city(self, cities):
        try:
            r = requests.get(self.url)
            resp = json.loads(r.content)
            ashrae_tmy_id = int(resp["outputs"]["ashrae_tmy"]["tmy_id"])  # don't know how to stop the unicode
            city = [c.name for c in cities if c.tmyid == ashrae_tmy_id][0]  # list index out of range if no match
            return city

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            debug_msg = "exc_type: {}; exc_value: {}; exc_traceback: {}".format(exc_type, exc_value.message,
                                                                                traceback.format_tb(exc_traceback))
            log.warning("Unable to get ASHRAE TMY ID from {}.".format(self.url))
            log.debug(debug_msg)
            return None
