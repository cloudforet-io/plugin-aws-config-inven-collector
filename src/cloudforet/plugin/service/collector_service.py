import logging

from spaceone.core.service import *

from cloudforet.plugin.manager.collector_manager import CollectorManager

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
            None
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

        return self.collector_mgr.verify_plugin(options, secret_data, schema)
