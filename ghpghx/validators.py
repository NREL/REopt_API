# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
import logging
from ghpghx.models import GHPGHXModel
from django.core.exceptions import ValidationError
log = logging.getLogger(__name__)

"""
Define reusable/importable django model validators to be used in
model fields option validators=[validator1, validator2, etc]

"""
