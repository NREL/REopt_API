import json
import copy

def convert_inputs(mgravens_inputs):
    # Format is (MG-RAVENS input, REopt input) with each as list of indexing in order of nesting high to low; 
    #    most are keys of the dictionary, and some are an array/list index. Include brackets for lists.
    required_inputs = [(['ProposedSiteLocation', 'Location.PositionPoints', '[0]', 'PositionPoint.xPosition'], ['Site', 'longitude']), 
                       (['ProposedSiteLocation', 'Location.PositionPoints', '[0]', 'PositionPoint.yPosition'], ['Site', 'latitude']),
                       (['LoadForecast', 'ResidentialGroup', 'ConformLoadGroup.ConformLoadSchedules', '[0]', 'RegularIntervalSchedule.TimePoints'], ['LoadForecast', 'Load'])]    
    # TODO handle multiple potential top level LoadForecast keys (ResGrp, IndGrp) and N number of 'ConformLoadGroup.ConformLoadSchedules'
    #   to add them all up into one array for ElectricLoad.loads_kw
    optional_inputs = [(['ProposedSiteLocation', 'ProposedSiteLocation.availableArea'], ['Site', 'land_acres'])]
    
    reopt_inputs = {}
    errors = {}
    warnings = {}

    missing = []
    unused = copy.deepcopy(mgravens_inputs)
    # Also create an "unused" mgravens_inputs dict by popping out all used values and returning the remainder
    for input in (required_inputs + optional_inputs):
        skip_rest = False
        try:
            # Find MG-RAVENS input value
            mgravens_input = convert_list_to_nested_index(input[0])
            try:
                mgravens_value = eval("mgravens_inputs" + mgravens_input)
            except:
                if input in required_inputs:
                    missing.append(input[0])
                skip_rest = True
            if skip_rest == False:
                exec("del unused"+mgravens_input)
                # Special inputs validation and processing/handling for different types
                #  E.g. for special validation use cases, converting array values, etc
                position_points = mgravens_inputs.get("Location.PositionPoints")
                if position_points and len(position_points) > 1:
                    warnings["required_inputs"] = "provided more than one Location.PositionPoints - REopt is going to use the first location entry"
                # If target mgravens_value is an array, loop through the array and pull relevant values
                if isinstance(mgravens_value, list):
                    regular_time_point_values = []
                    for timepoint in mgravens_value:
                        value1 = timepoint.get('RegularTimePoint.value1', None)
                        if value1 is not None:
                            regular_time_point_values.append(value1)
                    if regular_time_point_values:
                        mgravens_value = regular_time_point_values
                        
                # Assign to REopt input, build up the dictionary if not already
                add_keys_nested_dict(reopt_inputs, input[1])
                reopt_input = convert_list_to_nested_index(input[1])
                exec("reopt_inputs" + reopt_input + "= mgravens_value") # reopt_inputs[reopt_input] = mgravens_value
        except Exception as e:
            # This exception could be caused by either a missing required input or an unhandled error
            errors["unhandled"] = "Error occurred when processing input " + str(input) + " : " + repr(e)

            # Exception notes for future improvement
            # repr(e) gives you the exception(and the message string); str(e) only gives the message string.
            # If I had a logger, could use something like this:
            # logger.error('Example custom error message: %s', repr(e))

    if len(missing) != 0:
        errors["required_inputs"] = "The following required inputs are missing: " + str(missing)

    return reopt_inputs, errors, warnings, unused

def test_convert():

    with open("reoptjl/mgravens_inputs.json", "r") as file:
        mgravens_inputs = json.load(file)

    return convert_inputs(mgravens_inputs)

def add_keys_nested_dict(d, keys):
    for key in keys[:-1]:  # Even though keys[-1] is the last key, python skips the last key in this loop
        if key not in d.keys():
            d[key] = {}

def convert_list_to_nested_index(los):
    string_index = ""
    for key in los:
        if "[" in key:  # Indicates a list index instead of a dict key
            string_index += str(key)
        else:
            string_index += str("['" + key + "']")
        # print("los = ", string_index)
    return string_index


# Actually run the functions/code from above with example embedded in the test_convert() function
reopt_inputs, errors, warnings, unused = test_convert()
print("reopt_inputs = ", reopt_inputs)
print("errors = ", errors)
print("warnings = ", warnings)
print("unused = ", unused)