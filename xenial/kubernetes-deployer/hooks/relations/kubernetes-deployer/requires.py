#!/usr/bin/env python3
# Copyright (C) 2016  Ghent University
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
import json
import yaml

from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class KubernetesDeployerRequires(RelationBase):
    scope = scopes.GLOBAL

    @hook('{requires:kubernetes-deployer}-relation-{joined}')
    def joined(self):
        conv = self.conversation()
        conv.set_state('{relation_name}.joined')

    @hook('{requires:kubernetes-deployer}-relation-{changed}')
    def changed(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.joined')
        conv.set_state('{relation_name}.available')

    @hook('{requires:kubernetes-deployer}-relation-{departed,broken}')
    def broken(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.joined')
        conv.remove_state('{relation_name}.available')

    def send_external_service_requests(self, service_requests):
        """ service_requests: [
            {
                unit: <unit_name>,
                externalName: <ip or dns name>,
                ports: [<port>, ...]
            },
        ]
        """
        conv = self.conversation()
        conv.set_remote('external-service-requests', json.dumps(service_requests))

    def get_services(self, filter=True):
        conv = self.conversation()
        remote_services = yaml.safe_load(
            conv.get_remote('services', "{}"))
        if not filter:
            return remote_services
        filter = {}
        unit = os.environ['JUJU_UNIT_NAME'].split('/')[0]
        for key, value in remote_services.items():
            if unit == key:
                filter = value  # assumes only 1 service per unit
        return filter

    def send_headless_service_request(self, service_requests):
        """ service_request: {
                unit: <unit_name>,
                ips: [<ip>, ...],
                port: <port>
            }
        """
        conv = self.conversation()
        conv.set_remote('headless-service-requests', json.dumps(service_requests))

