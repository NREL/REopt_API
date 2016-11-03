from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpApplicationError

import library
import random
import os
from api_definitions import *

def default_dict_to_value(key_list,reference_dictionary, output_dictionary, default ):
    for k in key_list.keys():
        if k in reference_dictionary.keys():
            output_dictionary[k] = reference_dictionary.get(k)

        if output_dictionary.get(k) is None:
            output_dictionary[k] = default

    return output_dictionary

# We need a generic object to shove data in and to get data from.
class REoptObject(object):
    def __init__(self,id=None, inputDict=None, outputDict=None):

        inputs_ = {'source':inputs(just_required=True), "values":inputDict}
        outputs_ = {'source': outputs(), "values": outputDict}

        for group in [outputs_,inputs_]:
            for k in group['source'].keys():
                if group['values'] == None:
                    setattr(self, k, None)
                else:
                    print k, group['values'].get(k)
                    setattr(self, k, group['values'].get(k))
        self.id = id
        self.path_egg = get_egg()

class REoptRunResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the fields we're going to handle with the API here.

    # note, running process is from reopt_api head
    # i.e, C:\Nick\Projects\api\env\src\reopt_api

    input_fields = create_fields(inputs(just_required=True))
    output_fields = create_fields(outputs())

    class Meta:
        resource_name = 'reopt'
        allowed_methods = ['get', 'post']
        object_class = REoptObject
        authorization = Authorization()
        serializer = Serializer(formats=['json'])
        always_return_data = True

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj['id']

        return kwargs

    def get_id(self):
        return random.randint(0, 1000000)


    def get_object_list(self, request):

        id =  self.get_id()

        parsed_inputs = dict({i:request.GET.get(i) for i in inputs(just_required=True).keys()})

        run_set = library.DatLibrary(id,parsed_inputs)

        run_outputs = run_set.run()

        formatted_outputs = default_dict_to_value(outputs(),run_outputs,{},0)

        results = [REoptObject(id=id, inputDict=parsed_inputs, outputDict=formatted_outputs)]

        return results

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    # POST
    def obj_create(self, bundle, **kwargs):
        # Bundle is an object containing the posted json (within .data)
        data = bundle.data
        # Format Inputs for Optimization Run
        response_inputs = dict({k: data.get(k) for k in inputs(just_required=True).keys()})

        # Handle Rate Data
        blended_utility_rate = data.get('blended_utility_rate')
        demand_charge = data.get('demand_charge')
        urdb_rate = data.get('urdb_rate')

        # Create Dictionary
        id = self.get_id()
        run_set = library.DatLibrary(id, response_inputs)

        if urdb_rate is not None:
            run_set.parse_urdb(urdb_rate)

        elif (blended_utility_rate is not None) and (demand_charge is not None):
            urdb_rate = run_set.make_urdb_rate(blended_utility_rate, demand_charge)
            run_set.parse_urdb(urdb_rate)

        # Run Optimization
        run_outputs = run_set.run()

        # Handle Errors
        if run_set.timed_out:
            raise ImmediateHttpResponse(
                HttpApplicationError("Optimization model taking too long to respond!")
            )

        # Process Outputs
        formatted_inputs = dict({k:getattr(run_set, k) for k in inputs(just_required=True).keys()})
        formatted_outputs = dict({k:getattr(run_set, k) for k in outputs().keys()})
        formatted_outputs = default_dict_to_value(outputs(),formatted_outputs,{},0)

        # Package the bundle to return
        bundle.obj = REoptObject(id=id, inputDict=formatted_inputs, outputDict=formatted_outputs)

        # update fields with what was used
        for k in updates().keys():
            bundle.data[k] = getattr(bundle.obj,k)

        # update fields with what was used
        for k in outputs().keys():
            bundle.data[k] = formatted_outputs.get(k)

        return self.full_hydrate(bundle)
