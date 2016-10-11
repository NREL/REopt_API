from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie.serializers import Serializer

from log_levels import log
import logging

import library
import random
import os

# We need a generic object to shove data in and to get data from.
class REoptObject(object):
    def __init__(self, id=None, analysis_period=None, latitude=None, longitude=None, load_size=None, pv_om=None,
                 batt_cost_kw=None, batt_cost_kwh=None, load_profile=None, pv_cost=None, owner_discount_rate=None,
                 offtaker_discount_rate=None, utility_name=None, rate_name=None,
                 lcc=None, npv=None, utility_kwh=None, pv_kw=None, batt_kw=None, batt_kwh=None, load_8760_kwh=None,
                 load_monthly_kwh=None):

        self.id = id

        self.analysis_period = analysis_period
        self.latitude = latitude
        self.longitude = longitude
        self.load_size = load_size
        self.pv_om = pv_om
        self.batt_cost_kw = batt_cost_kw
        self.batt_cost_kwh = batt_cost_kwh
        self.load_profile = load_profile
        self.pv_cost = pv_cost
        self.owner_discount_rate = owner_discount_rate
        self.offtaker_discount_rate = offtaker_discount_rate
        self.utility_name = utility_name
        self.rate_name = rate_name
        self.load_8760_kwh = load_8760_kwh
        self.load_monthly_kwh = load_monthly_kwh

        # outputs
        self.lcc = lcc
        self.npv = npv
        self.utility_kwh = utility_kwh
        self.pv_kw = pv_kw
        self.batt_kw = batt_kw
        self.batt_kwh = batt_kwh


class REoptRunResource(Resource):
    # Just like a Django ``Form`` or ``Model``, we're defining all the
    # fields we're going to handle with the API here.

    # note, running process is from reopt_api head
    # i.e, C:\Nick\Projects\api\env\src\reopt_api

    # when deployed, runs from egg file, need to update if version changes!
    path_egg = os.path.join("..", "reopt_api-1.0-py2.7.egg")

    # when not deployed (running from 127.0.0.1:8000)
    # path_egg = os.getcwd()

    # input
    analysis_period = fields.IntegerField(attribute='analysis_period', null=True)
    latitude = fields.FloatField(attribute='latitude', null=True)
    longitude = fields.FloatField(attribute='longitude', null=True)
    load_size = fields.FloatField(attribute='load_size', null=True)
    load_8760_kwh = fields.ListField(attribute='load_8760_kwh', null=True)
    load_monthly_kwh = fields.ListField(attribute='load_monthly_kwh', null=True)
    pv_om = fields.FloatField(attribute='pv_om', null=True)
    batt_cost_kw = fields.FloatField(attribute='batt_cost_kw', null=True)
    batt_cost_kwh = fields.FloatField(attribute='batt_cost_kwh', null=True)
    load_profile = fields.CharField(attribute='load_profile', null=True)
    pv_cost = fields.FloatField(attribute='pv_cost', null=True)
    owner_discount_rate = fields.FloatField(attribute='owner_discount_rate', null=True)
    offtaker_discount_rate = fields.FloatField(attribute='offtaker_discount_rate', null=True)
    utility_name = fields.CharField(attribute='utility_name', null=True)
    rate_name = fields.CharField(attribute='rate_name', null=True)

    # internally generated
    id = fields.IntegerField(attribute='id')

    #outputs
    lcc = fields.FloatField(attribute="lcc", null=True)
    npv = fields.FloatField(attribute="npv", null=True)
    utility_kwh = fields.FloatField(attribute="utility_kwh", null=True)
    pv_kw = fields.FloatField(attribute="pv_kw", null=True)
    batt_kw = fields.FloatField(attribute="batt_kw", null=True)
    batt_kwh = fields.FloatField(attribute="batt_kwh", null=True)

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

        # generate a unique id for this run
        run_id = random.randint(0, 1000000)

        analysis_period = request.GET.get("analysis_period")
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
        load_size = request.GET.get("load_size")
        pv_om = request.GET.get("pv_om")
        batt_cost_kw = request.GET.get("batt_cost_kw")
        batt_cost_kwh = request.GET.get("batt_cost_kwh")
        load_profile = request.GET.get("load_profile")
        pv_cost = request.GET.get("pv_cost")
        owner_discount_rate = request.GET.get("owner_discount_rate")
        offtaker_discount_rate = request.GET.get("offtaker_discount_rate")
        utility_name = request.GET.get("utility_name")
        rate_name = request.GET.get("rate_name")

        run_set = library.DatLibrary(run_id, self.path_egg, analysis_period, latitude, longitude, load_size, pv_om,
                                     batt_cost_kw, batt_cost_kwh, load_profile, pv_cost, owner_discount_rate,
                                     offtaker_discount_rate, utility_name, rate_name)
        outputs = run_set.run()

        lcc = 0
        npv = 0
        utility_kwh = 0
        pv_kw = 0
        batt_kw = 0
        batt_kwh = 0

        if 'lcc' in outputs:
            lcc = outputs['lcc']
        if 'npv' in outputs:
            npv = outputs['lcc']
        if 'utility_kwh' in outputs:
            utility_kwh = outputs['utility_kwh']
        if 'pv_kw' in outputs:
            pv_kw = outputs['pv_kw']
        if 'batt_kw' in outputs:
            batt_kw = outputs['batt_kw']
        if 'batt_kwh' in outputs:
            batt_kwh = outputs['batt_kwh']

        results = []
        new_obj = REoptObject(run_id, analysis_period, latitude, longitude, load_size, pv_om, batt_cost_kw,
                              batt_cost_kwh, load_profile, pv_cost, owner_discount_rate, offtaker_discount_rate,
                              utility_name, rate_name, lcc, npv, utility_kwh, pv_kw, batt_kw, batt_kwh)
        results.append(new_obj)
        return results

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    # POST
    def obj_create(self, bundle, **kwargs):

        # generate a unique id for this run
        run_id = random.randint(0, 1000000)

        analysis_period = latitude = longitude = load_size = pv_om = batt_cost_kw = batt_cost_kwh = load_profile = None
        load_size = pv_om = batt_cost_kw = batt_cost_kwh = load_profile = pv_cost = owner_discount_rate = None
        offtaker_discount_rate = utility_name = rate_name = blended_utility_rate = demand_charge = urdb_rate = None
        load_8760_kwh = load_monthly_kwh = None

        use_urdb = False

        # bundle is an object containing the posted json (within .data)
        data = bundle.data
        if 'analysis_period' in data:
            analysis_period = data['analysis_period']
        if 'latitude' in data:
            latitude = data['latitude']
        if 'longitude' in data:
            longitude = data['longitude']
        if 'load_size' in data:
            load_size = data['load_size']
        if 'pv_om' in data:
            pv_om = data['pv_om']
        if 'batt_cost_kw' in data:
            batt_cost_kw = data['batt_cost_kw']
        if 'batt_cost_kwh' in data:
            batt_cost_kwh = data['batt_cost_kwh']
        if 'load_profile' in data:
            load_profile = data['load_profile']
        if 'load_8760_kwh' in data:
            load_8760_kwh = data['load_8760_kwh']
        if 'load_monthly_kwh' in data:
            load_monthly_kwh = data['load_monthly_kwh']
        if 'pv_cost' in data:
            pv_cost = data['pv_cost']
        if 'owner_discount_rate' in data:
            owner_discount_rate = data['owner_discount_rate']
        if 'offtaker_discount_rate' in data:
            offtaker_discount_rate = data['offtaker_discount_rate']
        if 'utility_name' in data:
            utility_name = data['utility_name']
        if 'rate_name' in data:
            rate_name = data['rate_name']
        if "blended_utility_rate" in data:
            blended_utility_rate = data["blended_utility_rate"]
        if 'demand_charge' in data:
            demand_charge = data['demand_charge']
        if 'urdb_rate' in data:
            urdb_rate = data['urdb_rate']
            use_urdb = True

        run_set = library.DatLibrary(run_id, self.path_egg, analysis_period, latitude, longitude, load_size, pv_om,
                                     batt_cost_kw, batt_cost_kwh, load_profile, pv_cost, owner_discount_rate,
                                     offtaker_discount_rate, utility_name, rate_name, load_8760_kwh, load_monthly_kwh)

        if use_urdb:
            run_set.parse_urdb(urdb_rate)
        elif (blended_utility_rate is not None) and (demand_charge is not None):
            urdb_rate = run_set.make_urdb_rate(blended_utility_rate, demand_charge)
            run_set.parse_urdb(urdb_rate)

        outputs = run_set.run()

        lcc = npv = utility_kwh = pv_kw = batt_kw = batt_kwh = 0
        if 'lcc' in outputs:
            lcc = outputs['lcc']
        if 'npv' in outputs:
            npv = outputs['npv']
        if 'utility_kwh' in outputs:
            utility_kwh = outputs['utility_kwh']
        if 'pv_kw' in outputs:
            pv_kw = outputs['pv_kw']
        if 'batt_kw' in outputs:
            batt_kw = outputs['batt_kw']
        if 'batt_kwh' in outputs:
            batt_kwh = outputs['batt_kwh']

        new_obj = REoptObject(run_id, run_set.analysis_period, latitude, longitude, run_set.load_size, run_set.pv_om,
                              run_set.batt_cost_kw, run_set.batt_cost_kwh, load_profile, run_set.pv_cost,
                              run_set.rate_owner_discount, run_set.rate_offtaker_discount, utility_name, rate_name,
                              lcc, npv, utility_kwh, pv_kw, batt_kw, batt_kwh, load_8760_kwh,
                              load_monthly_kwh)

        # package the bundle to return
        bundle.obj = new_obj

        # update fields with what was used
        bundle.data['load_size'] = new_obj.load_size
        bundle.data['pv_cost'] = new_obj.pv_cost
        bundle.data['pv_om'] = new_obj.pv_om
        bundle.data['batt_cost_kw'] = new_obj.batt_cost_kw
        bundle.data['batt_cost_kwh'] = new_obj.batt_cost_kwh
        bundle.data['owner_discount_rate'] = new_obj.owner_discount_rate
        bundle.data['offtaker_discount_rate'] = new_obj.offtaker_discount_rate
        bundle.data['analysis_period'] = new_obj.analysis_period

        bundle = self.full_hydrate(bundle)
        return bundle
