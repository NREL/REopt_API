from django.db import models


class Resilience(models.Model):

    load_8760_kw = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])
    pv_resource = ArrayField(models.TextField(blank=True), null=True, blank=True, default=[])

