import requests
import json
import os
import urllib
import pandas
import random

class urdb_download:
    # API specific
    key = "BLLsYv81d8y4w6UPYCfGFsuWlu4IujlZYliDmoq6"
    base = "http://api.openei.org/utility_rates?version=3&format=json&detail=full"
    url_base = base + "&api_key=" + key

    # Input data
    utilities = []
    rates = []
    lines = []

    # Output
    output_root = []

    def __init__(self, output_root):
        self.output_root = output_root


    def load_urdb_rate_list(self,file):
        self.utility_df = pandas.DataFrame.from_csv(file)
        self.utilities = self.utility_df['utility'].values
        self.rates = self.utility_df['name'].values

    def read_input_txt_file(self, input_file):
        with open(input_file, 'r') as f:
            for n, line_unstripped in enumerate(f):
                line = line_unstripped.strip()
                try:
                    semi_colon = line.index(';')
                    self.utilities.append(line[0:semi_colon])
                    self.rates.append(line[semi_colon + 2:])
                    self.lines.append(line)
                    # print('{}; {}'.format(line[0:semi_colon], line[semi_colon + 1:]))
                except:
                    print('\033[91mLine {} of input file does not contains a semi-colon.\033[0m'.format(n+1))

    def get_rates(self, sample_rate=1):

        output = {}
        all_utilities = random.sample(self.utilities , int( len(self.utilities) * sample_rate ) )

        for utility in all_utilities:
            # we have to replace & to handle url correctly
            utility_string = urllib.quote_plus(utility)
            url = self.url_base + "&ratesforutility=" + utility_string
            r = requests.get(url, verify=False)

            response = json.loads(r.text, strict=False)
            output[utility] = response['items']

        return output