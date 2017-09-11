from models import URDBError

def log_urdb_errors(label, errors, warnings):
    #dictionary of id: warning
    for e in errors:
    	if not bool(URDBError.objects.filter(label = label, type="Error", message= e)):
        	e = URDBError(label = label, type="Error", message= e)
        	e.save()
    
    for w in warnings:
    	if not bool(URDBError.objects.filter(label = label, type="Warning", message= w)):
	        w = URDBError(label = label, type="Warning", message= w)
	        w.save()
