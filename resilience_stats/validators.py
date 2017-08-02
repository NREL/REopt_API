# https://docs.djangoproject.com/en/1.8/ref/validators/
from django.core.exceptions import ValidationError


def validate_RunOutput_for_outage_simulator(ro):
    if ro.pv_kw is None:
        raise ValidationError('Scenario pv_kw undefined')

    if ro.batt_kwh is None:
        raise ValidationError('Scenario batt_kwh undefined')

    if ro.batt_kw is None:
        raise ValidationError('Scenario batt_kw undefined')

    if ro.load_8760_kw is None:
        raise ValidationError('Scenario load profile undefined')

    if ro.pv_kw_ac_hourly is None:
        raise ValidationError('Scenario PV production undefined')

    if ro.year_one_battery_soc_series is None:
        raise ValidationError('Scenario battery state-of-charge undefined')

    if ro.crit_load_factor is None:
        raise ValidationError('Scenario critical load factor undefined')

    if ro.batt_efficiency is None:
        raise ValidationError('Scenario battery efficiency undefined')

    if ro.batt_inverter_efficiency is None:
        raise ValidationError('Scenario battery inverter efficiency undefined')

    if ro.batt_rectifier_efficiency is None:
        raise ValidationError('Scenario battery rectifier efficiency undefined')

    if len(ro.load_8760_kw) != len(ro.year_one_battery_soc_series):
        raise ValidationError('Scenario load profile does not have the same number of time steps as battery state-of-charge')
