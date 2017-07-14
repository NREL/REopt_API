from django.db import models
from pro_forma_writer import ProFormaWriter
import uuid
import os


class ProForma(models.Model):

    run_input_id = models.IntegerField(null=False)
    uuid = models.UUIDField(default=uuid.uuid4, null=False)


    def make(self, **kwargs):
        # change ProFormaWriter to accept kwargs

        cash_flow = ProFormaWriter(self.uuid, **kwargs)
        cash_flow.update_template()
        cash_flow.compute_cashflow()

