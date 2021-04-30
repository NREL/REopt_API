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
import json
import os
import copy
import numpy as np
from tastypie.test import ResourceTestCaseMixin
from unittest import TestCase  # have to use unittest.TestCase to get tests to store to database, django.test.TestCase flushes db
from reo.models import ModelManager
from reo.utilities import MMBTU_TO_KWH, TONHOUR_TO_KWHT

class GHPTest(ResourceTestCaseMixin, TestCase):
    REopt_tol = 1e-2

    def setUp(self):
        super(GHPTest, self).setUp()
        self.reopt_base = '/v1/job/'
        self.loads_view = '/v1/simulated_load/'
        self.test_post = os.path.join('reo', 'tests', 'posts', 'test_ghp_POST.json')

    def get_reopt_response(self, data):
        return self.api_client.post(self.reopt_base, format='json', data=data)
    
    def get_loads_response(self, params_dict):
        return self.api_client.get(self.loads_view, data=params_dict)

    def test_ghp(self):
        """

        GHP Testing

        """

        # TODO insert call to GHPGHX app to run GHP model and return the "ghp_response" as input to REopt
        #   this would mimick the process the webtool (and API users) would call GHPGHX then REopt

        # Call API, get results in "d" dictionary
        nested_data = json.load(open(self.test_post, 'rb'))
        nested_data["Scenario"]["timeout_seconds"] = 420  # Overwriting
        nested_data["Scenario"]["optimality_tolerance_techs"] = 0.01  # Overwriting
        nested_data["Scenario"]["optimality_tolerance_bau"] = 0.001

        # Get load data from /simulated_load endpoint using the self.test_post location and building type
        latitude = nested_data["Scenario"]["Site"]["latitude"]
        longitude = nested_data["Scenario"]["Site"]["longitude"]
        doe_reference_name = nested_data["Scenario"]["Site"]["LoadProfileBoilerFuel"]["doe_reference_name"]
        heating_params = {"latitude": latitude,
                            "longitude": longitude,
                            "doe_reference_name": doe_reference_name,
                            "load_type": "heating"}
        cooling_params = copy.deepcopy(heating_params)
        cooling_params["load_type"] = "cooling"
        cooling_params["chiller_cop"] = nested_data["Scenario"]["Site"]["LoadProfileChillerThermal"]["chiller_cop"]
        
        heating_load_resp = self.get_loads_response(params_dict=heating_params)  # This is FUEL-based
        heating_load_dict = json.loads(heating_load_resp.content)
        boiler_effic = nested_data["Scenario"]["Site"]["Boiler"]["boiler_efficiency"]
        heating_load_thermal = list(np.array(heating_load_dict["loads_mmbtu"]) * boiler_effic)
        cooling_load_resp = self.get_loads_response(params_dict=cooling_params)
        cooling_load_dict = json.loads(cooling_load_resp.content)
        cooling_load_thermal = cooling_load_dict["loads_ton"]

        # Estimate electric consumption from GHP based on heating and cooling load and estimated COPs
        heating_cop = 2.5
        cooling_cop = 4.5
        ghp_heating_elec = np.array(heating_load_thermal) * MMBTU_TO_KWH / heating_cop
        ghp_cooling_elec = np.array(cooling_load_thermal) * TONHOUR_TO_KWHT / cooling_cop
        ghp_elec = list(ghp_heating_elec + ghp_cooling_elec)
        ghx_pump_elec = list(0.05 * (ghp_heating_elec + ghp_cooling_elec))

        # Add mock ghp_response, 2 design options
        # 2nd design option serves a fraction of the loads with a fraction of the size, so
        #   it assumes that the existing Boiler and ElectricChiller can serve the remainder of the load
        case2_size_fraction = 0.5
        nested_data["Scenario"]["Site"]["GHP"]["ghpghx_response"].append({"ghp_uuid": "1aaa",
                                                                        "inputs":{
                                                                            "heating_thermal_load_mmbtu_per_hr": heating_load_thermal,
                                                                            "cooling_thermal_load_ton": cooling_load_thermal
                                                                        },
                                                                        "outputs":{
                                                                            "n_bores": 400.0,
                                                                            "length_boreholes": 600.0,
                                                                            "yearly_heatpump_electric_consumption_series_kw": ghp_elec,
                                                                            "yearly_ghx_pump_electric_consumption_series_kw": ghx_pump_elec
                                                                        }})

        nested_data["Scenario"]["Site"]["GHP"]["ghpghx_response"].append({"ghp_uuid": "2bbb",
                                                                        "inputs":{
                                                                            "heating_thermal_load_mmbtu_per_hr": [case2_size_fraction * heating_load_thermal[i] for i in range(len(heating_load_thermal))],
                                                                            "cooling_thermal_load_ton": [case2_size_fraction * cooling_load_thermal[i] for i in range(len(cooling_load_thermal))]
                                                                        },
                                                                        "outputs":{
                                                                            "n_bores": case2_size_fraction * 400.0,
                                                                            "length_boreholes": 600.0,
                                                                            "yearly_heatpump_electric_consumption_series_kw": [case2_size_fraction * ghp_elec[i] for i in range(len(ghp_elec))],
                                                                            "yearly_ghx_pump_electric_consumption_series_kw": [case2_size_fraction * ghx_pump_elec[i] for i in range(len(ghx_pump_elec))]
                                                                        }})                                                                        
        
        # Call REopt
        #json.dump(nested_data, open("ghp_post.json", "w"))
        resp = self.get_reopt_response(data=nested_data)
        json.dumps(nested_data)
        self.assertHttpCreated(resp)
        r = json.loads(resp.content)
        run_uuid = r.get('run_uuid')
        d = ModelManager.make_response(run_uuid=run_uuid)

        ghp_uuid = d["outputs"]["Scenario"]["Site"]["GHP"]["ghp_chosen_uuid"]
        print("GHP uuid chosen = ", ghp_uuid)

        #TODO index into the ghp_response with ghp_uuid to get GHP results
        # Could add actual index to outputs to index on list_of_dict instead, but that would be redundant
        # could instead get ghp_uuid after getting index of list_of_dict, but maybe we could instead do a 
        # ModelManager call in process_results to assign the chosen ghp_response
