# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for creating forwarding rules."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages

from googlecloudsdk.compute.lib import base_classes


SUPPORTED_PROTOCOLS = sorted(
    messages.ForwardingRule.IPProtocolValueValuesEnum.to_dict().keys())


class CreateForwardingRule(base_classes.BaseAsyncMutator):
  """Create a forwarding rule to direct network traffic to a load balancer."""

  @staticmethod
  def Args(parser):
    address = parser.add_argument(
        '--address',
        help='The external IP address that the forwarding rule will serve.')
    address.detailed_help = """\
        The external IP address that the forwarding rule will
        serve. All traffic sent to this IP address is directed to the
        virtual machines that are in the target pool pointed to by the
        forwarding rule. If the value is a reserved IP address, the
        address must live in the same region as the forwarding rule. If
        this flag is omitted, an ephemeral IP address is assigned.
        """

    ip_protocol = parser.add_argument(
        '--ip-protocol',
        choices=SUPPORTED_PROTOCOLS,
        help='The IP protocol that the rule will serve.')
    ip_protocol.detailed_help = """\
        The IP protocol that the rule will serve. If left empty, TCP
        is used. Supported protocols are: {0}.
        """.format(', '.join(SUPPORTED_PROTOCOLS))

    parser.add_argument(
        '--description',
        help='An optional textual description for the forwarding rule.')

    port_range = parser.add_argument(
        '--port-range',
        help=('If specified, only packets addressed to ports in the specified '
              'range will be forwarded.'),
        metavar='PORT-PORT')
    port_range.detailed_help = """\
        If specified, only packets addressed to ports in the specified
        range will be forwarded. If not specified, all ports are
        matched.
        """

    parser.add_argument(
        '--region',
        help='The region in which the forwarding rule will be created')

    target = parser.add_mutually_exclusive_group(required=True)

    target_instance = target.add_argument(
        '--target-instance',
        help='The target instance that will receive the traffic.')
    target_instance.detailed_help = """\
        The target instance that will receive the traffic. The target
        instance must be in a zone that's part of the forwarding
        rule's region. The value of this flag can be either the URI of
        the target instance or a suffix of it containing the zone such
        as ``us-central2-a/targetInstances/my-target-instance''.
        """

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
    return 'Insert'

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

    if args.ip_protocol:
      protocol = messages.ForwardingRule.IPProtocolValueValuesEnum(
          args.ip_protocol)
    else:
      protocol = None

    request = messages.ComputeForwardingRulesInsertRequest(
        forwardingRule=messages.ForwardingRule(
            description=args.description,
            name=forwarding_rule_context['forwardingRule'],
            IPAddress=args.address,
            IPProtocol=protocol,
            portRange=args.port_range,
            target=target,
        ),
        project=forwarding_rule_context['project'],
        region=forwarding_rule_context['region'])
    return [request]


CreateForwardingRule.detailed_help = {
    'brief': ('Create a forwarding rule to direct network traffic to a load '
              'balancer'),
    'DESCRIPTION': """\
        *{command}* is used to create a forwarding rule. Forwarding
        rules match and direct certain types of traffic to a load
        balancer which is controlled by a target pool or a single
        instance that is controlled by a target instance. For more
        information on load balancing, see
        link:https://developers.google.com/compute/docs/load-balancing/[].

        When creating a forwarding rule, either ``--target-instance''
        or ``--target-pool'' must be specified.
        """,
}

