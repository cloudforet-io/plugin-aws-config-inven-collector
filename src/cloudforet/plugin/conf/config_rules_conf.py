CONFIG_RULES = {
    'AUTOSCALING_GROUP_ELB_HEALTHCHECK_REQUIRED': {
        'description': 'Checks if your Auto Scaling groups that are associated with a Classic Load Balancer are using Elastic Load Balancing health checks. The rule is NON_COMPLIANT if the Auto Scaling groups are not using Elastic Load Balancing health checks.',
        'trigger_type': 'Configuration changes'
    }
}
