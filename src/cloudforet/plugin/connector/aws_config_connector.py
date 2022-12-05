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

    def describe_conformance_pack_compliance(self, pack_name: str):
        response = self.client.describe_conformance_pack_compliance(ConformancePackName=pack_name)
        return response.get('ConformancePackRuleComplianceList', [])

    def get_compliance_details_by_config_rule(self, rule_name: str):
        return self.client.get_compliance_details_by_config_rule(ConfigRuleName=rule_name)

    def get_conformance_pack_compliance_details(self, pack_name: str, results: List[dict] = None,
                                                next_token: str = None):
        results = results or []
        kwargs = {
            'ConformancePackName': pack_name
        }

        if next_token:
            kwargs['NextToken'] = next_token

        response = self.client.get_conformance_pack_compliance_details(**kwargs)
        results += response.get('ConformancePackRuleEvaluationResults', [])

        if 'NextToken' in response:
            self.get_conformance_pack_compliance_details(pack_name, results, response['NextToken'])

        return results

    def describe_config_rules(self, rule_names: List[str]):
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
