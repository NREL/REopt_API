from django.http import JsonResponse
from reo.models import ScenarioModel
from models import ResilienceModel
from reo.utilities import API_Error

def resilience_stats(request):
    uuid = request.GET.get('run_uuid')

    try:
        scenario = ScenarioModel.objects.filter(run_uuid=uuid).first()
    
    except Exception as e:
        return API_Error(e).response

    rm = ResilienceModel.create(scenario_model=scenario)

    site = scenario.sitemodel_set().first()
    batt = site.storagemodel_set.first()
    pv = site.pvmodel_set.first()
    load_profile = site.loadprofile_set.first()

    batt_roundtrip_efficiency = batt.internal_efficiency_pct \
                                * batt.inverter_efficiency_pct\
                                * batt.rectifier_efficiency_pct
    
    results = simulate_outage(
        pv_kw = pv.size_kw,
        batt_kwh = batt.size_kwh,
        batt_kw = batt.size_kw,
        load = load_profile.year_one_electric_load_series_kw,
        pv_kw_ac_hourly = pv.year_one_power_production_series_kw,
        init_soc = batt.year_one_soc_series_pct,
        crit_load_factor = load_profile.critical_load_pct,
        batt_roundtrip_efficiency= batt_roundtrip_efficiency,
    )
    

    rm.update(results)
    rm.save()
    
    response = JsonResponse(results)
    return response
