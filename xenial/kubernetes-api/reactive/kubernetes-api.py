#!/usr/bin/env python3
# Copyright (C) 2017  Ghent University
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from charmhelpers.core import hookenv, unitdata
from charmhelpers.core.hookenv import status_set, log
from charms.reactive import when, when_not, set_state, remove_state


@when('dockerhost.available')
@when_not('api.installed')
def install_k8s_api(dockerhost):
    if not conf['controller_ip'] or not conf['user'] or not conf['password']:
        status_set('blocked', 'Please fill in all configs')
        return
    unitdata.kv().set('docker-image-env', {
        'controller_ip': conf['controller_ip'],
        'user': conf['juju_user'],
        'password': conf['juju_password'],
        'model_uuid': os.environ['JUJU_MODEL_UUID'],
    })
    set_state('docker-image.start')
    set_state('api.installed')


@when('dockerhost.available',
      'endpoint.available')
@when_not('api.running')
def configure_endpoint(dockerhost, endpoint):
    conf = hookenv.config()
    log("Checking if container is running")
    containers = dockerhost.get_running_containers()  # Werkt dit als er meerdere docker image charms verbonden zijn?
    log(containers)
    unit_name = os.environ['JUJU_UNIT_NAME'].split('/')[0]
    if unit_name in containers:  # Check if container is from this app
        # Return example:
        # {'api': {'ports': {'5000': 31832}, 'service_name': 'api-service.default', 'host': 'juju-c41e8b-43'}}
        port = list(containers[unit_name]['ports'].values())[0]  # Random port
        host = containers[unit_name]['host']
        endpoint.configure(port=port, hostname=host, private_address=host)
        set_state('api.running')
