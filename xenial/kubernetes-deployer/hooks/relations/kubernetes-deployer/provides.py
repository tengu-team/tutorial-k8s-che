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

import json
import yaml
from charmhelpers.core import hookenv
from charms.reactive import hook
from charms.reactive import RelationBase
from charms.reactive import scopes


class KubernetesDeployerProvides(RelationBase):
    scope = scopes.UNIT

    @hook('{provides:kubernetes-deployer}-relation-{joined,changed}')
    def changed(self):
        self.set_state('{relation_name}.available')

    @hook('{provides:kubernetes-deployer}-relation-{departed}')
    def broken(self):
        self.remove_state('{relation_name}.available')

    @property
    def external_service_requests(self):
        requests = []
        for conv in self.conversations():
            conv_req = yaml.safe_load(
                conv.get_remote('external-service-requests', "[]"))
            if conv_req:
                requests.append(conv_req)
        return requests

    @property
    def headless_service_requests(self):
        requests = []
        for conv in self.conversations():
            conv_req = yaml.safe_load(
                conv.get_remote('headless-service-requests', "{}"))
            if conv_req:
                requests.append(conv_req)
        return requests

    def send_services(self, services):
        """ There is no way to send each unit only the containers it requested due to limitations
        in Juju. Even with scope=UNIT, the same data is still broadcasted to all units of a single
        service. See https://tinyurl.com/hjwfwdn """
        for conv in self.conversations():
            conv.set_remote('services', json.dumps(services))
