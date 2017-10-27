from django.db import models
from django.contrib.postgres.fields import ArrayField
from reo.models import REoptResponse
from outage_simulator import simulate_outage
from validators import validate_RunOutput_for_outage_simulator


class ResilienceModel(models.Model):

    run_output = models.ForeignKey(REoptResponse)

    resilience_by_timestep = ArrayField(models.FloatField(null=True), null=True)
    resilience_hours_min = models.FloatField(null=True)
    resilience_hours_max = models.FloatField(null=True)
    resilience_hours_avg = models.FloatField(null=True)
    outage_durations = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving = ArrayField(models.FloatField(null=True), null=True)

    @classmethod
    def create(cls, **kwargs):
        rm = cls(**kwargs)
        validate_RunOutput_for_outage_simulator(rm.run_output)
    
        cls.batt_roundtrip_efficiency = rm.run_output.batt_efficiency\
                                    * rm.run_output.batt_inverter_efficiency\
                                    * rm.run_output.batt_rectifier_efficiency
        
        results = simulate_outage(
            pv_kw=rm.run_output.pv_kw,
            batt_kwh=rm.run_output.batt_kwh,
            batt_kw=rm.run_output.batt_kw,
            load=rm.run_output.load_8760_kw,
            pv_kw_ac_hourly=rm.run_output.pv_kw_ac_hourly,
            init_soc=rm.run_output.year_one_battery_soc_series,
            crit_load_factor=rm.run_output.crit_load_factor,
            batt_roundtrip_efficiency=cls.batt_roundtrip_efficiency,
        )
        
        rm.resilience_by_timestep = results.get('resilience_by_timestep')
        rm.resilience_hours_min = results.get('resilience_hours_min')
        rm.resilience_hours_max = results.get('resilience_hours_max')
        rm.resilience_hours_avg = results.get('resilience_hours_avg')
        rm.outage_durations = results.get('outage_durations')
        rm.probs_of_surviving = results.get('probs_of_surviving')

        rm.save()
        return rm
