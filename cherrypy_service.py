"""
The most basic (working) CherryPy 3.1 Windows service possible.
Requires Mark Hammond's pywin32 package.
"""

import cherrypy
import win32serviceutil
import win32service

class HelloWorld:
    """ Sample request handler class. """

    @cherrypy.expose
    def index(self):
        return "Hello world!"
    

class MyService(win32serviceutil.ServiceFramework):
    """NT Service."""
    
    _svc_name_ = "CherryPyService"
    _svc_display_name_ = "CherryPy Service"

    def SvcDoRun(self):
        cherrypy.tree.mount(HelloWorld(), '/')
        
        # in practice, you will want to specify a value for
        # log.error_file below or in your config file.  If you
        # use a config file, be sure to use an absolute path to
        # it, as you can't be assured what path your service
        # will run in.
        cherrypy.config.update({
            'global':{
                'log.screen': False,
                'engine.autoreload.on': False,
                'engine.SIGHUP': None,
                'engine.SIGTERM': None
                }
            })
        
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