# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for setting targets on forwarding rules."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages

from googlecloudsdk.compute.lib import base_classes


class SetTarget(base_classes.BaseAsyncMutator):
  """Set the target of a forwarding rule."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--region',
        help='The region of the forwarding rule.')

    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        '--target-instance',
        help='The target instance that will receive the traffic.')

    target.add_argument(
        '--target-pool',
        help='The target pool that will receive the traffic.')

    target.detailed_help = """\
        The target pool that will receive the traffic. The target pool
        must be in the same region as the forwarding rule.
        """

    parser.add_argument(
        'name',
        help='The name of the forwarding rule.')

  @property
  def service(self):
    return self.context['compute'].forwardingRules

  @property
  def method(self):
    return 'SetTarget'

  @property
  def print_resource_type(self):
    return 'forwardingRules'

  def CreateRequests(self, args):
    forwarding_rule_context = self.context['path-handler'].Parse(
        'forwardingRules', args.name, region=args.region)

    if args.target_pool:
      target = self.context['path-handler'].Normalize(
          'targetPools', args.target_pool,
          region=forwarding_rule_context['region'])
    else:
      target = self.context['path-handler'].Normalize(
          'targetInstances', args.target_instance,
          zone=None)

    request = messages.ComputeForwardingRulesSetTargetRequest(
        forwardingRule=forwarding_rule_context['forwardingRule'],
        project=forwarding_rule_context['project'],
        region=forwarding_rule_context['region'],
        targetReference=messages.TargetReference(
            target=target,
        ))
    return [request]


SetTarget.detailed_help = {
    'brief': ('Set the target of a forwarding rule'),
    'DESCRIPTION': """\
        *{command}* is used to change the target of a forwarding
        rule.
        """,
}

