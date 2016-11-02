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

        if output_dictionary.get(k) == None:
            output_dictionary[k] = default

    return output_dictionary

# We need a generic object to shove data in and to get data from.
class REoptObject(object):
    def __init__(self,inputDict, outputDict, internalDict):

        inputs_ = {'source':inputs(just_required=True), "values":inputDict}
        internal_ = {'source': internals(), "values": internalDict}
        outputs_ = {'source': outputs(), "values": outputDict}

        for group in [inputs_,internal_,outputs_]:
            for k in group['source'].keys():
                setattr(self, k, group['values'][k])

class REoptRunResource(Resource,egg="reopt_api-1.0-py2.7.egg"):
    # Just like a Django ``Form`` or ``Model``, we're defining all the fields we're going to handle with the API here.

    # note, running process is from reopt_api head
    # i.e, C:\Nick\Projects\api\env\src\reopt_api

    # when deployed, runs from egg file, need to update if version changes!
    path_egg = os.path.join("..", egg)

    # when not deployed (running from 127.0.0.1:8000)  path_egg = os.getcwd()

    input_fields = create_fields(inputs(just_required=True))
    internal_fields = create_fields(internals())
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

    def get_object_list(self, request):

        parsed_inputs = dict({i:request.GET.get(i) for i in inputs(just_required=True).keys()})

        run_set = library.DatLibrary(parsed_inputs, set_internal(path_egg))

        run_outputs = run_set.run()

        formatted_outputs = default_dict_to_value(outputs(),run_outputs,{},0)

        results = [REoptObject(run_id, parsed_inputs, formatted_outputs)]

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
        run_set = library.DatLibrary(response_inputs,set_internal(path_egg))

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
        formatted_inputs = dict({k:run_set.get(k) for k in inputs(just_required=True).keys()})
        formatted_outputs = default_dict_to_value(outputs(),run_outputs,{},0)

        # Package the bundle to return
        bundle.obj = REoptObject(formatted_inputs, formatted_outputs, internal)

        # update fields with what was used
        for k in updates().keys():
            bundle.data[k] = bundle.obj.get(k)

        return self.full_hydrate(bundle)
