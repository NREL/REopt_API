import cherrypy
import os
from reopt_api import settings
from djangoplugin import DjangoAppPlugin

class DjangoApplication(object):
    def run(self):
        cherrypy.config.update({
            'global':{
                'server.socket_file': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tmp/cherrypy.sock'),
                'log.screen': True,
                'engine.autoreload.on': False,
                'engine.SIGHUP': None,
                }
            })

        os.environ['DJANGO_SETTINGS_MODULE'] = 'reopt_api.settings'
        DjangoAppPlugin(cherrypy.engine, settings).subscribe()

        cherrypy.engine.start()
        cherrypy.engine.block()

if __name__ == '__main__':
    DjangoApplication().run()
