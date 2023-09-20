# REopt®, Copyright (c) Alliance for Sustainable Energy, LLC. See also https://github.com/NREL/REopt_API/blob/master/LICENSE.
from .models import URDBError
import subprocess

def log_urdb_errors(label, errors=[], warnings=[]):
    #dictionary of id: warning
    
    existing = False
    
    try:
        existing = URDBError.objects.filter(label = label, type="Error")
    except:
        pass

    if not bool(existing) and len(errors) > 0:
        for e in errors:
            e = URDBError(label = label, type="Error", message= e)
            e.save_to_db()
    
    if len(warnings) > 0:
        for w in warnings:
            if not bool(URDBError.objects.filter(label = label, type="Warning", message= w)):
                w = URDBError(label = label, type="Warning", message= w)
                w.save_to_db()

