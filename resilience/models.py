from django.db import models
from django.contrib.postgres.fields import *


class ResilienceCase(models.Model):

    load_8760_kwh = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    pv_resource_kwh = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    api_version = models.TextField(blank=True, default='', null=False)

