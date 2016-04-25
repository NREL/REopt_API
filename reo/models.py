from django.db import models

# Create your models here.
class REoptRun(models.Model):
    npv = models.FloatField(default=0.0)
    lcc = models.FloatField(default=0.0)


