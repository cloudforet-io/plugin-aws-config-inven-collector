import logging
from typing import Generator

from spaceone.core.service import *
from spaceone.core.error import *

from cloudforet.plugin.manager.collector_manager import CollectorManager
from cloudforet.plugin.manager.aws_config_manager import AWSConfigManager

_LOGGER = logging.getLogger(__name__)


class CollectorService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collector_mgr: CollectorManager = self.locator.get_manager(CollectorManager)

    @transaction
    @check_required(['options'])
    def init(self, params):
        """ init plugin by options

        Args:
            params (dict): {
                'options': 'dict',
                'domain_id': 'str'
            }

        Returns:
            plugin_data (dict)
        """

        options = params.get('options', {})

        return self.collector_mgr.init_response(options)

    @transaction
    @check_required(['options', 'secret_data'])
    def verify(self, params):
        """ Verifying collector plugin

        Args:
            params (dict): {
                'options': 'dict',
                'schema': 'str',
                'secret_data': 'dict',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        options = params['options']
        secret_data = params['secret_data']
        schema = params.get('schema')

        self.collector_mgr.create_session(options, secret_data, schema)

    @transaction
    @check_required(['options', 'secret_data'])
    def collect(self, params):
        """ Collect external data

        Args:
            params (dict): {
                'options': 'dict',
                'schema': 'str',
                'secret_data': 'dict',
                'domain_id': 'str'
            }

        Returns:
            generator of resource_data (dict)
        """

        options = params['options']
        secret_data = params['secret_data']
        schema = params.get('schema')

        session = self.collector_mgr.create_session(options, secret_data, schema)
        regions = self.collector_mgr.list_regions()

        aws_config_mgr: AWSConfigManager = self.locator.get_manager(AWSConfigManager, session=session)

        for region_name in regions:
            for resource_data in aws_config_mgr.collect(options, region_name):
                yield resource_data
