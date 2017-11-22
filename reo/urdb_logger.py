
from models import URDBError
import os
from django.conf import settings

def log_urdb_errors(label, errors, warnings):
    #dictionary of id: warning

    if not bool(URDBError.objects.filter(label = label, type="Error")):
        try:
    	    subject = 'REopt flagged International URDB Rate - {}'.format(label)
    	    message = 'Hello,\n\n This is an automated message from REopt. The following issue(s) came up recently with international URDB rate {}: \n\n{}\n\nThanks for looking into this,\n\nThe REopt Team\nREopt@nrel.gov'.format(label, errors)
    	    from_address = 'no-reply@reopt.nrel.gov'
    	    command = 'echo -e "{}" | mail -s "{}" -r "{}" {}'.format(message,subject,from_address, " ".join(settings.URDB_NOTIFICATION_EMAIL_LIST))
    	    os.system(command)
        except:
            pass  

    	for e in errors:
    	    e = URDBError(label = label, type="Error", message= e)
            e.save()
    
    for w in warnings:
    	if not bool(URDBError.objects.filter(label = label, type="Warning", message= w)):
	        w = URDBError(label = label, type="Warning", message= w)
	        w.save()
