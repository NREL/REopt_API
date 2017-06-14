import cherrypy
import os

env = os.environ['APP_ENV']
if env == 'development':
    from reopt_api import dev_settings as settings
elif env == 'staging':
    from reopt_api import staging_settings as settings
else:
    raise TypeError('Unknown APP_ENV')

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

        DjangoAppPlugin(cherrypy.engine, settings).subscribe()

        cherrypy.engine.start()
        cherrypy.engine.block()

if __name__ == '__main__':
    DjangoApplication().run()
