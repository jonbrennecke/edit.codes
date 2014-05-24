# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for creating target instances."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import resolvers


class Create(base_classes.BaseAsyncMutator):
  """Create a target instance for handling traffic from a forwarding rule."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--description',
        help='An optional, textual description of the target instance.')
    parser.add_argument(
        '--instance',
        required=True,
        help=('The name of the virtual machine instance that will handle the '
              'traffic.'))

    zone = parser.add_argument(
        '--zone',
        help=('The zone of the target instance (i.e., where the instance '
              'resides).'))
    zone.detailed_help = """\
        The zone of the target instance (i.e., where the instance
        resides). This flag can be omitted if the zone is included in
        the ``--instance'' flag (e.g.,
        ``us-central2-a/instances/my-instance'') or in the name of the
        target instance (e.g., ``us-central2-a/instances/my-target-instance'').
        """
    parser.add_argument(
        'name',
        help='The name of the target instance.')

  @property
  def service(self):
    return self.context['compute'].targetInstances

  @property
  def method(self):
    return 'Insert'

  @property
  def print_resource_type(self):
    return 'targetInstances'

  def RegisterCustomResolvers(self):
    self.context['path-handler'].RegisterResolver(
        'instances', 'zone', resolvers.GetZoneFromArgumentsOrTargetInstance)
    self.context['path-handler'].RegisterResolver(
        'targetInstances', 'zone', resolvers.GetZoneFromArgumentsOrInstance)

  def CreateRequests(self, args):
    self.RegisterCustomResolvers()

    target_instance_context = self.context['path-handler'].Parse(
        'targetInstances', args.name, zone=args.zone,
        related_instance=args.instance)

    instance_uri = self.context['path-handler'].Normalize(
        'instances', args.instance, zone=args.zone,
        related_target_instance=args.name)

    request = messages.ComputeTargetInstancesInsertRequest(
        targetInstance=messages.TargetInstance(
            description=args.description,
            name=target_instance_context['targetInstance'],
            instance=instance_uri,
        ),
        project=target_instance_context['project'],
        zone=target_instance_context['zone'])

    return [request]


Create.detailed_help = {
    'brief': (
        'Create a target instance for handling traffic from a forwarding rule'),
    'DESCRIPTION': """\
        *{command}* is used to create a target instance for handling
        traffic from one or more forwarding rules. Target instances
        are ideal for traffic that should be managed by a single
        source. For more information on target instances, see
        link:https://developers.google.com/compute/docs/protocol-forwarding/#targetinstances[].
        """,
}

