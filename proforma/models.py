# *********************************************************************************
# REopt, Copyright (c) 2019-2020, Alliance for Sustainable Energy, LLC.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or other
# materials provided with the distribution.
#
# Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
# *********************************************************************************
from django.db import models
import uuid
import os
import datetime, tzlocal
from reo.models import ScenarioModel
import logging
from proforma.proforma_generator import generate_proforma
log = logging.getLogger(__name__)


class ProForma(models.Model):

    scenariomodel = models.OneToOneField(
        ScenarioModel,
        on_delete=models.CASCADE,
        default=0,
        to_field='id',
        blank=True,
        primary_key=True
    )
    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    spreadsheet_created = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    @classmethod
    def create(cls, scenariomodel, **kwargs ):
        pf = cls(scenariomodel = scenariomodel, **kwargs)
        file_dir = os.path.dirname(pf.output_file)
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        pf.save()        
        return pf
    
    @property
    def sheet_io(self):
        return "Inputs and Outputs"

    @property
    def output_file_name(self):
        return "ProForma.xlsm"

    @property
    def output_file(self):
        folder = os.path.join(os.getcwd(),'static', 'files', str(self.uuid))
        if not os.path.exists(folder):
            os.mkdir(folder)
        return os.path.join(folder, self.output_file_name)
          
    def generate_spreadsheet(self):
        log.info("Generating proforma spreadsheet")
        generate_proforma(self.scenariomodel, self.output_file)
        self.spreadsheet_created = tzlocal.get_localzone().localize(datetime.datetime.now())
        return True
