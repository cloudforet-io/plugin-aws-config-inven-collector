import logging
from typing import List

from cloudforet.plugin.connector.aws_boto_connector import AWSBotoConnector

__all__ = ['AWSConfigConnector']

_LOGGER = logging.getLogger(__name__)


class AWSConfigConnector(AWSBotoConnector):

    def init_client(self, region_name: str):
        self.client = self.session.client('config', region_name=region_name)

    def describe_conformance_packs(self):
        response = self.client.describe_conformance_packs()
        return response.get('ConformancePackDetails', [])

    def describe_conformance_pack_compliance(self, pack_name):
        response = self.client.describe_conformance_pack_compliance(ConformancePackName=pack_name)
        return response.get('ConformancePackRuleComplianceList', [])

    def describe_config_rules(self, rule_names):
        config_rules = []
        for items in self._page_by_size(rule_names, 25):
            response = self.client.describe_config_rules(ConfigRuleNames=items)
            config_rules += response.get('ConfigRules', [])

        return config_rules

    @staticmethod
    def _page_by_size(items: List[str], size: int):
        page_count = int(len(items) / size) + 1

        for num in range(page_count):
            offset = size * num
            yield items[offset:offset + size]
