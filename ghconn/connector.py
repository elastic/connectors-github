#
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. Licensed under the Elastic License 2.0;
# you may not use this file except in compliance with the Elastic License 2.0.
#
import os

from connectors.source import BaseDataSource
from ghconn.client import get_files


class GithubDataSource(BaseDataSource):

    @classmethod
    def get_default_configuration(cls):
        return {
            "token": {
                "value": os.environ.get('GH_TOKEN', ''),
                "label": "Github Token",
                "type": "str",
            },
            "owner": {
                "value": "elastic",
                "label": "Github owner",
                "type": "str",
            },
            "repository": {
                "value": "elasticsearch",
                "label": "Github repository",
                "type": "str",
            },

        }

    async def ping(self):
        pass

    async def get_docs(self, filtering=None):
        token = self.configuration['token']
        owner = self.configuration['owner']
        repository = self.configuration['repository']
        async for doc in get_files(token, owner, repository):
            yield doc
