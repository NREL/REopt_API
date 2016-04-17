from django.db import models

# Create your models here.
class REoptRun(models.Model):
    net_present_value = models.FloatField(default=0.0)

