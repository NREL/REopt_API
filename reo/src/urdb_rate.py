# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
#! usr/bin/python
"""
Rate class for URDB rates.
Inputs are: util, rate
rate can be either name string or label string.
If name string is used then the newest rate is found.
(There are redundant rate names in URDB, but not redundant labels.)

NOTE:
    The URDB API version affects the rate label.
    version=3 is US URDB
    version=4 is International URDB
    The same rate will have different labels between versions 3 and 4!

The Rate class checks a local JSON cache for desired rate before checking URDB.
If rate cache does not exist it makes a new one and adds the rate to it.

Example usage:

my_rate1 = Rate(rate='574e02195457a343795e629e')
my_rate2 = Rate(rate='Residential Time of Use', util='United Power, Inc')

"""
import requests
import json
import logging
log = logging.getLogger(__name__)

# cache_file = "rate_cache.json"
# try:
#     with open(cache_file, 'rb') as f:
#         rate_cache = json.load(f)
#
# except ValueError as e:
#     log("INFO", "Could not find rate cache. Making new {}.".format(cache_file))
#     rate_cache = dict()
# except IOError:
#     log("INFO", "Could not find rate cache. Making new {}.".format(cache_file))
#     rate_cache = dict()


class Rate(object):

    def __init__(self, rate, util=None):
        """
        :param rate: str, rate name (must include util name) or rate label
        :param util: str, optional
        """
        self.util = util
        self.rate = rate  # rate name string

        self.urdb_dict = self.get_rate() # can return None

    def get_rate(self):

        # try:
        #     rate_dict = rate_cache[self.rate]
        #     log("INFO", 'Found rate in cache.')
        #
        # except KeyError:
        rate_dict = self.download_rate()
        if rate_dict is not None:
            log.info('Found rate in URDB.')
                # self.add_rate_to_cache(rate_dict, rate_cache)
        else:
            return None

        try:
            if rate_dict['energyratestructure'] is None:
                rate_dict = None
        except KeyError:
            rate_dict = None

        return rate_dict

    def download_rate(self):
        """
        Check URDB for rate.
        :return: Either rate dict or None
        """

        url_base = "http://api.openei.org/utility_rates?"
        api_key = "BLLsYv81d8y4w6UPYCfGFsuWlu4IujlZYliDmoq6"
        request_params = {
            "version": "7",
            "format": "json",
            "detail": "full",
            "api_key": api_key,
        }

        using_rate_label = False

        if " " not in self.rate or self.util is None:  # no spaces in rate label, assume spaces in rate name
            request_params["getpage"] = self.rate
            using_rate_label = True

        else:
            # have to replace '&' to handle url correctly
            request_params["ratesforutility"] = self.util.replace("&", "%26")

        log.info('Checking URDB for {}...'.format(self.rate))
        res = requests.get(url_base, params=request_params, verify=False)

        if not res.ok:
            log.debug('URDB response not OK. Code {} with message: {}'.format(res.status_code, res.text))
            raise Warning('URDB response not OK.')
            # return None

        data = json.loads(res.text, strict=False)
        rates_in_util = data['items']  # data['items'] contains a list of dicts, one dict for each rate in util

        if len(rates_in_util) == 0:
            log.info('Could not find {} in URDB.'.format(self.rate))
            return None

        if not using_rate_label:
            matched_rates = []
            start_dates = []

            for rate in rates_in_util:

                if rate['name'] == self.rate:
                    matched_rates.append(rate)  # urdb can contain multiple rates of same name

                    if 'startdate' in rate:
                        start_dates.append(rate['startdate'])

            # find the newest rate of those that match the self.rate
            newest_index = 0

            if len(start_dates) > 1 and len(start_dates) == len(matched_rates):
                newest_index = start_dates.index(max(start_dates))

            if len(matched_rates) > 0:
                newest_rate = matched_rates[newest_index]
                return newest_rate
            else:
                log.info('Could not find {} in URDB.'.format(self.rate))
                return None

        elif rates_in_util[0]['label'] == self.rate:
            return rates_in_util[0]

        else:
            log.info('Could not find {} in URDB'.format(self.rate))
            return None

    # @staticmethod
    # def add_rate_to_cache(rate, cache):
    #
    #     cache[rate['label']] = rate
    #     with open(cache_file, 'wb') as f:
    #         json.dump(cache, f)
