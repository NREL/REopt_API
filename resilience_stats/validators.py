# https://docs.djangoproject.com/en/1.8/ref/validators/
from django.core.exceptions import ValidationError


def validate_RunOutput_for_outage_simulator(ro):
    if ro.pv_kw is None:
        raise ValidationError('proforma validators','Scenario pv_kw undefined')

    if ro.batt_kwh is None:
        raise ValidationError('proforma validators','Scenario batt_kwh undefined')

    if ro.batt_kw is None:
        raise ValidationError('proforma validators','Scenario batt_kw undefined')

    if ro.load_8760_kw is None:
        raise ValidationError('proforma validators','Scenario load profile undefined')

    if ro.pv_kw > 0 and ro.pv_kw_ac_hourly is None:
        raise ValidationError('proforma validators','Scenario PV production undefined (with pv_kw > 0)')

    if ro.crit_load_factor is None:
        raise ValidationError('proforma validators','Scenario critical load factor undefined')

    if ro.batt_kw > 0 and ro.batt_efficiency is None:
        raise ValidationError('proforma validators','Scenario battery efficiency undefined (with batt_kw > 0)')

    if ro.batt_kw > 0 and ro.batt_inverter_efficiency is None:
        raise ValidationError('proforma validators','Scenario battery inverter efficiency undefined (with batt_kw > 0)')

    if ro.batt_kw > 0 and ro.batt_rectifier_efficiency is None:
        raise ValidationError('proforma validators','Scenario battery rectifier efficiency undefined (with batt_kw > 0)')

    if ro.year_one_battery_soc_series is not None:
        if len(ro.load_8760_kw) != len(ro.year_one_battery_soc_series):
            raise ValidationError('proforma validators','Scenario load profile does not have the same number of time steps as battery state-of-charge')
