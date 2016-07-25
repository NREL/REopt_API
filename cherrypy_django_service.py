"""
The most basic (working) CherryPy 3.1 Windows service possible.
Requires Mark Hammond's pywin32 package.
"""

import cherrypy
import win32serviceutil
import win32service
import os
from reopt_api import settings
from djangoplugin import DjangoAppPlugin

class MyService(win32serviceutil.ServiceFramework):
    """NT Service."""
    
    _svc_name_ = "CherryPyService"
    _svc_display_name_ = "CherryPy Service"

    def SvcDoRun(self):
        # in practice, you will want to specify a value for
        # log.error_file below or in your config file.  If you
        # use a config file, be sure to use an absolute path to
        # it, as you can't be assured what path your service
        # will run in.
        cherrypy.config.update({
            'global':{
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 80,
                'log.screen': False,
                'log.error_file': 'C:\\Nick\\Projects\\api\env\\src\\reopt_api\\cherry.log',
                'engine.autoreload.on': False,
                'engine.SIGHUP': None,
                'engine.SIGTERM': None
                }
            })
        
        os.environ['DJANGO_SETTINGS_MODULE'] = 'reopt_api.settings'
        DjangoAppPlugin(cherrypy.engine, settings).subscribe()
        
        cherrypy.engine.start()
        cherrypy.engine.block()
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        cherrypy.engine.exit()
        
        self.ReportServiceStatus(win32service.SERVICE_STOPPED) 
        # very important for use with py2exe
        # otherwise the Service Controller never knows that it is stopped !
        
if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyService)