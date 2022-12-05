import logging
from typing import Generator, List, Literal

from cloudforet.plugin.manager.collector_manager import CollectorManager
from cloudforet.plugin.connector.aws_config_connector import AWSConfigConnector
from cloudforet.plugin.model.cloud_service_model import CloudService

_LOGGER = logging.getLogger(__name__)


class AWSConfigManager(CollectorManager):

    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aws_connector: AWSConfigConnector = self.locator.get_connector(AWSConfigConnector)
        self.aws_connector.session = session
        self.cloud_service_group = 'Compliance'
        self.cloud_service_type = 'AWS-CIS-v1_4-LV1'

    def collect(self, options: dict, region_name: str) -> Generator[dict, None, None]:
        self.region_name = region_name
        _LOGGER.debug(f'[AWSConfigManager.collect] ({region_name}) collecting resources..')

        allowed_pack_names = options.get('conformance_pack_names')

        try:
            self.aws_connector.init_client(region_name)
            packs = self.aws_connector.describe_conformance_packs()
            pack_names = self._filter_conformance_packs(packs, allowed_pack_names)

            count = 0
            for pack_name in pack_names:
                for resource_data in self._list_conformance_rules(pack_name):
                    yield self.make_response(resource_data)
                    count += 1

            _LOGGER.debug(f'[AWSConfigManager.collect] ({region_name}) resource count: {count}')

        except Exception as e:
            yield self.error_response(e)

    def _list_conformance_rules(self, pack_name: str):
        rules = self.aws_connector.describe_conformance_pack_compliance(pack_name)
        rule_names = [rule['ConfigRuleName'] for rule in rules]

        config_rules = self.aws_connector.describe_config_rules(rule_names)

        for item in config_rules:
            print(item)

        for item in rules:
            resource_data = {
                'name': item['ConfigRuleName'],
                'reference': {
                    # 'resource_id': item['ConfigRuleId']
                },
                'data': {
                    'state': self._get_rule_state(item['ComplianceType']),
                    # 'arn': item['ConfigRuleArn'],
                    'compliance': {
                        'compliance_type': item['ComplianceType'],
                    },
                    'conformance_pack': {
                        'name': pack_name
                    }
                },
                'metadata': {}
            }

            yield self.validate_cloud_service(resource_data)

    @staticmethod
    def _get_rule_state(compliance_type: str) -> Literal['PASS', 'FAILED']:
        if compliance_type == 'NON_COMPLIANT':
            return 'FAILED'
        else:
            return 'PASS'

    @staticmethod
    def _filter_conformance_packs(packs: List[dict], allowed_pack_names: List[str]) -> List[str]:
        allowed_packs = []
        for pack in packs:
            pack_name = pack['ConformancePackName']
            if allowed_pack_names:
                if pack_name in allowed_pack_names:
                    allowed_packs.append(pack_name)
            else:
                allowed_packs.append(pack_name)

        return allowed_packs
