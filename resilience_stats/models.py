from django.db import models
from django.contrib.postgres.fields import ArrayField
from reo.models import ScenarioModel
from outage_simulator import simulate_outage
from validators import validate_RunOutput_for_outage_simulator


class ResilienceModel(models.Model):

    scenario_model = models.ForeignKey(
        ScenarioModel,
        to_field = 'run_uuid',
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

    @classmethod
    def create(cls, scenario_model, **kwargs):
        
        rm = cls(scenario_model=scenario_model, **kwargs)
        rm.save()
        return rm
