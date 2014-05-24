# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding instances to target pools."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import resolvers


class AddInstance(base_classes.BaseAsyncMutator):
  """Add instances to a target pool."""

  @staticmethod
  def Args(parser):
    instances = parser.add_argument(
        '--instances',
        help='Specifies a list of instances to add to the target pool.',
        metavar='INSTANCE',
        nargs='+',
        required=True)
    instances.detailed_help = """\
        Specifies a list of instances that will receive traffic directed to
        this target pool. Each entry must be specified by a relative or
        fully-qualified path to the instance (e.g.,
        ``--instances us-central1-a/instances/my-instance'').
        All instances in one target pool must belong to the same region as
        the target pool.
        Instances do not need to exist at the time the target pool is created
        and can be created afterwards.
        """

    parser.add_argument(
        '--region',
        help='The region of the target pool.')

    parser.add_argument(
        'name',
        help='The name of the target pool to which to add the instances.')

  @property
  def service(self):
    return self.context['compute'].targetPools

  @property
  def method(self):
    return 'AddInstance'

  @property
  def print_resource_type(self):
    return 'targetPools'

  def CreateRequests(self, args):
    self.context['path-handler'].RegisterResolver(
        'instances', 'zone', resolvers.RequireExplicitZone)

    target_pool_context = self.context['path-handler'].Parse(
        'targetPools', args.name, region=args.region)

    instances = [
        self.context['path-handler'].Normalize(
            'instances', instance, user_input=instance)
        for instance in args.instances]

    request = messages.ComputeTargetPoolsAddInstanceRequest(
        region=target_pool_context['region'],
        project=target_pool_context['project'],
        targetPool=target_pool_context['targetPool'],
        targetPoolsAddInstanceRequest=messages.TargetPoolsAddInstanceRequest(
            instances=[messages.InstanceReference(
                instance=inst) for inst in instances]))

    return [request]


AddInstance.detailed_help = {
    'brief': 'Add instances to a target pool',
    'DESCRIPTION': """\
        *{command}* is used to add one or more instances to a target pool.
        For more information on health checks and load balancing, see
        link:https://developers.google.com/compute/docs/load-balancing/[].
        """,
}

