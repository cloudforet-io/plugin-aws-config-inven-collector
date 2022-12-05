import logging
from typing import Generator, List, Literal

from spaceone.core import utils
from cloudforet.plugin.conf.config_rules_conf import CONFIG_RULES
from cloudforet.plugin.manager.collector_manager import CollectorManager
from cloudforet.plugin.connector.aws_config_connector import AWSConfigConnector
from cloudforet.plugin.model.aws_config_model.cloud_service import CloudService
from cloudforet.plugin.model.aws_config_model.cloud_service_type import CloudServiceType

_LOGGER = logging.getLogger(__name__)


class AWSConfigManager(CollectorManager):

    def __init__(self, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aws_connector: AWSConfigConnector = self.locator.get_connector(AWSConfigConnector)
        self.aws_connector.session = session
        self.cloud_service_group = 'Compliance'
        self.cloud_service_type = 'CIS-AWS-1.4'

    def collect(self, options: dict, region_name: str) -> Generator[dict, None, None]:
        self.region_name = region_name
        _LOGGER.debug(f'[AWSConfigManager.collect] ({region_name}) collecting resources..')

        allowed_pack_names = options.get('conformance_pack_names')

        try:
            self.aws_connector.init_client(region_name)

            cloud_service_type = CloudServiceType()
            yield self.make_response(cloud_service_type.dict(),
                                     {'1': ['name', 'group', 'provider']},
                                     resource_type='inventory.CloudServiceType')

            account_id = self.aws_connector.get_account_id()
            pack_map = self._get_conformance_pack_map(allowed_pack_names)

            count = 0
            for pack_name, pack_info in pack_map.items():
                evaluation_results_map = self._get_evaluation_results_map(pack_name)

                for resource_data in self._list_conformance_rules(account_id, pack_name, pack_info,
                                                                  evaluation_results_map):
                    yield self.make_response(resource_data,
                                             {'1': [
                                                 'reference.resource_id',
                                                 'provider',
                                                 'cloud_service_type',
                                                 'cloud_service_group',
                                                 'account'
                                             ]})
                    count += 1

            _LOGGER.debug(f'[AWSConfigManager.collect] ({region_name}) resource count: {count}')

        except Exception as e:
            yield self.error_response(e)

    def _get_conformance_pack_map(self, allowed_pack_names: List[str]) -> dict:
        packs = self.aws_connector.describe_conformance_packs()

        pack_map = {}
        for pack in packs:
            pack_name = pack['ConformancePackName']
            if allowed_pack_names and pack_name not in allowed_pack_names:
                pass
            else:
                pack_map[pack_name] = {
                    'name': pack['ConformancePackName'],
                    'arn': pack['ConformancePackArn'],
                    'pack_id': pack['ConformancePackId'],
                    'input_parameters': pack.get('ConformancePackInputParameters', []),
                    'last_update_request_time': utils.datetime_to_iso8601(pack['LastUpdateRequestedTime'])
                }

        return pack_map

    def _get_evaluation_results_map(self, pack_name: str) -> dict:
        evaluation_results = self.aws_connector.get_conformance_pack_compliance_details(pack_name)
        evaluation_results_map = {}

        for evaluation_result in evaluation_results:
            rule_name = evaluation_result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ConfigRuleName']
            if rule_name not in evaluation_results_map:
                evaluation_results_map[rule_name] = []

            evaluation_results_map[rule_name].append(evaluation_result)

        return evaluation_results_map

    def _list_conformance_rules(self, account_id: str, pack_name: str, pack_info: str, evaluation_results_map: dict):
        rules = self.aws_connector.describe_conformance_pack_compliance(pack_name)
        config_rule_map = self._get_config_rule_map(rules)

        for item in rules:
            config_rule = config_rule_map.get(item['ConfigRuleName'], {})
            evaluation_results = evaluation_results_map.get(item['ConfigRuleName'], [])
            results_info, failed_resource_count = self._get_evaluation_results(evaluation_results)
            resource_data = {
                'name': item['ConfigRuleName'],
                'reference': {
                    'resource_id': config_rule.get('arn')
                },
                'data': {
                    'status': self._get_rule_state(item['ComplianceType']),
                    'compliance': {
                        'compliance_type': item['ComplianceType'],
                    },
                    'conformance_pack': pack_info,
                    'resources': results_info,
                    'failed_resource_count': failed_resource_count
                },
                'region_code': self.region_name,
                'account': account_id
            }

            resource_data['data'].update(config_rule)

            cloud_service = CloudService(**resource_data)
            yield cloud_service.dict()

    @staticmethod
    def _get_evaluation_results(evaluation_results: List[dict]) -> [List[dict], int]:
        results_info = []
        failed_resource_count = 0
        for evaluation_result in evaluation_results:
            if evaluation_result['ComplianceType'] == 'NON_COMPLIANT':
                failed_resource_count += 1

            resource_info = evaluation_result['EvaluationResultIdentifier']['EvaluationResultQualifier']
            result_info = {
                'compliance_type': evaluation_result['ComplianceType'],
                'resource_type': resource_info['ResourceType'],
                'resource_id': resource_info['ResourceId'],
            }

            if 'Annotation' in evaluation_result:
                result_info['annotation'] = evaluation_result['Annotation']

            results_info.append(result_info)

        return results_info, failed_resource_count

    def _get_config_rule_map(self, rules: List[dict]) -> dict:
        rule_names = [rule['ConfigRuleName'] for rule in rules]
        config_rules = self.aws_connector.describe_config_rules(rule_names)

        config_rule_map = {}

        for item in config_rules:
            rule_name = item['ConfigRuleName']
            config_rule_map[rule_name] = {
                'rule_id': item['ConfigRuleId'],
                'name': rule_name,
                'arn': item['ConfigRuleArn'],
                'scope': self._get_scope_from_config_rule(item.get('Scope', {})),
                'source': self._get_source_from_config_rule(item.get('Source', {}))
            }

        return config_rule_map

    @staticmethod
    def _get_scope_from_config_rule(scope: dict) -> dict:
        scope_info = {
            'compliance_resource_types': scope.get('ComplianceResourceTypes', []),
        }

        if 'ComplianceResourceId' in scope:
            scope_info['compliance_resource_id'] = scope['ComplianceResourceId']

        if 'TagKey' in scope:
            scope_info['tag_key'] = scope['TagKey']

        if 'TagValue' in scope:
            scope_info['tag_value'] = scope['TagValue']

        return scope_info

    @staticmethod
    def _get_source_from_config_rule(source: dict) -> dict:
        identifier = source['SourceIdentifier']
        source_info = {
            'owner': source['Owner'],
            'owner_display': 'AWS managed' if source['Owner'] == 'AWS' else 'Custom',
            'source_identifier': identifier
        }

        if source['Owner'] == 'AWS':
            source_details = CONFIG_RULES.get(identifier, {})
            source_info.update(source_details)

        return source_info

    @staticmethod
    def _get_rule_state(compliance_type: str) -> Literal['PASS', 'FAILED']:
        if compliance_type == 'NON_COMPLIANT':
            return 'FAILED'
        else:
            return 'PASS'
