# -*- coding: utf-8 -*-
import imp
import os, os.path
import urlparse

import cherrypy
from cherrypy.process import plugins

import django
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler

from httplogger import HTTPLogger

__all__ = ['DjangoAppPlugin']

class DjangoAppPlugin(plugins.SimplePlugin):
    def __init__(self, bus, settings_module, wsgi_http_logger=HTTPLogger):
        """ CherryPy engine plugin to configure and mount
        the Django application onto the CherryPy server.
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.settings_module = settings_module
        self.wsgi_http_logger = wsgi_http_logger

    def start(self):
        """ When the bus starts, the plugin is also started
        and we load the Django application. We then mount it on
        the CherryPy engine for serving as a WSGI application.
        We let CherryPy serve the application's static files.
        """
        cherrypy.log("Loading and serving the Django application")
        cherrypy.tree.graft(self.wsgi_http_logger(WSGIHandler()))
        settings_module = self.settings_module

        # App specific static handler
        static_handler = cherrypy.tools.staticdir.handler(
            section="/",
            dir=os.path.split(settings_module.STATIC_ROOT)[1],
            root=os.path.abspath(os.path.split(settings_module.STATIC_ROOT)[0])
        )
        cherrypy.tree.mount(static_handler, settings_module.STATIC_URL)

        # Admin static handler. From django's internal (django.core.servers.basehttp)
        admin_static_dir = os.path.join(django.__path__[0], 'contrib', 'admin', 'static')
        admin_static_handler = cherrypy.tools.staticdir.handler(
            section='/',
            dir='admin',
            root=admin_static_dir
        )
        cherrypy.tree.mount(admin_static_handler, urlparse.urljoin(settings_module.STATIC_URL, 'admin'))
