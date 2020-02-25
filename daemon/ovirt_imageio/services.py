# ovirt-imageio
# Copyright (C) 2015-2020 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from __future__ import absolute_import

import logging

from . import extents
from . import http
from . import images
from . import pki
from . import profile
from . import ssl
from . import tickets
from . import uhttp
from . import util

log = logging.getLogger("services")


class Service(object):

    name = None

    def start(self):
        util.start_thread(self._run, name=self.name)

    def stop(self):
        log.debug("Stopping %s", self.name)
        self._server.shutdown()

    @property
    def port(self):
        return self._server.server_port

    @property
    def address(self):
        return self._server.server_address

    def _run(self):
        log.debug("Starting %s", self.name)
        self._server.serve_forever(
            poll_interval=self._config.daemon.poll_interval)
        log.debug("%s terminated normally", self.name)


class RemoteService(Service):
    """
    Service used to access images data from remote host.

    Access to this service requires a valid ticket that can be installed using
    the local control service.
    """

    name = "remote.service"

    def __init__(self, config):
        self._config = config
        self._server = http.Server(
            (config.images.host, config.images.port),
            http.Connection)
        # TODO: Make clock configurable, disabled by default.
        self._server.clock_class = util.Clock
        if config.images.port == 0:
            config.images.port = self.port
        self._secure_server()
        self._server.app = http.Router([
            (r"/images/(.*)/extents", extents.Handler(config)),
            (r"/images/(.*)", images.Handler(config)),
        ])
        log.debug("%s listening on port %d", self.name, self.port)

    def _secure_server(self):
        key_file = pki.key_file(self._config)
        cert_file = pki.cert_file(self._config)
        log.debug("Securing server (certfile=%s, keyfile=%s)",
                  cert_file, key_file)
        context = ssl.server_context(
            cert_file, cert_file, key_file,
            enable_tls1_1=self._config.daemon.enable_tls1_1)
        self._server.socket = context.wrap_socket(
            self._server.socket, server_side=True)


class LocalService(Service):
    """
    Service used to access images locally.

    Access to this service requires a valid ticket that can be installed using
    the control service.
    """

    name = "local.service"

    def __init__(self, config):
        self._config = config
        self._server = uhttp.Server(config.images.socket, uhttp.Connection)
        # TODO: Make clock configurable, disabled by default.
        self._server.clock_class = util.Clock
        if config.images.socket == "":
            config.images.socket = self.address
        self._server.app = http.Router([
            (r"/images/(.*)/extents", extents.Handler(config)),
            (r"/images/(.*)", images.Handler(config)),
        ])
        log.debug("%s listening on %r", self.name, self.address)


class ControlService(Service):
    """
    Service used to control imageio daemon on a host.

    The service is using unix socket owned by a program managing the host. Only
    this program can access the socket.
    """

    name = "control.service"

    def __init__(self, config):
        self._config = config
        self._server = uhttp.Server(config.tickets.socket, uhttp.Connection)
        # TODO: Make clock configurable, disabled by default.
        self._server.clock_class = util.Clock
        if config.tickets.socket == "":
            config.tickets.socket = self.address
        self._server.app = http.Router([
            (r"/tickets/(.*)", tickets.Handler(config)),
            (r"/profile/", profile.Handler(config)),
        ])
        log.debug("%s listening on %r", self.name, self.address)