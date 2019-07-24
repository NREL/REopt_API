from django.db import models
from django.contrib.postgres.fields import ArrayField, HStoreField
from reo.models import ScenarioModel


class ResilienceModel(models.Model):

    scenariomodel = models.OneToOneField(
        ScenarioModel,
        to_field='id',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True
    )

    resilience_by_timestep = ArrayField(models.FloatField(null=True), null=True)
    resilience_hours_min = models.FloatField(null=True)
    resilience_hours_max = models.FloatField(null=True)
    resilience_hours_avg = models.FloatField(null=True)
    outage_durations = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving = ArrayField(models.FloatField(null=True), null=True)
    probs_of_surviving_by_month = ArrayField(ArrayField(models.FloatField(null=True), null=True), null=True)
    probs_of_surviving_by_hour_of_the_day = ArrayField(ArrayField(models.FloatField(null=True), null=True), null=True)
    present_worth_factor = models.FloatField(null=True)
    avg_critical_load = models.FloatField(null=True)
    survives_specified_outage = models.NullBooleanField()

    @classmethod
    def create(cls, scenariomodel, **kwargs):
        
        rm = cls(scenariomodel=scenariomodel, **kwargs)
        rm.save()
        return rm
