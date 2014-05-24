# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for getting a target pool's health."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import request_helper


class GetHealth(base_classes.BaseGetter):
  """Get the health of instances in a target pool."""

  @staticmethod
  def Args(parser):
    base_classes.BaseGetter.Args(parser, add_name_regex_arg=False)
    base_classes.AddFieldsFlag(parser, 'targetPoolInstanceHealth')

    instances = parser.add_argument(
        '--instances',
        default=[],
        nargs='+',
        help='The set of instances in the pool to display health status for.')
    instances.detailed_help = """\
        The set of instances in the pool to display health status for. If not
        provided, health checks for all instances in the pool are displayed. Each
        value must be a full URI of an instance or a suffix of the URI that includes
        the zone (e.g., ``us-central2-a/instance/my-instance'').
        """

    parser.add_argument(
        '--region',
        help='The region of the target pool.')

    parser.add_argument(
        'name',
        help='The name of the target pool.')

  @property
  def service(self):
    return self.context['compute'].targetPools

  @property
  def print_resource_type(self):
    return 'targetPoolInstanceHealth'

  def GetTargetPool(self, target_pool_context):
    """Fetches the target pool resource."""
    objects = list(request_helper.MakeRequests(
        requests=[(self.service,
                   'Get',
                   messages.ComputeTargetPoolsGetRequest(
                       project=target_pool_context['project'],
                       region=target_pool_context['region'],
                       targetPool=target_pool_context['targetPool']))],
        http=self.context['http'],
        batch_url=self.context['batch-url']))

    return objects[0]

  def GetResources(self, args, errors):
    """Returns a list of targetPoolInstanceHealth objects."""
    target_pool_context = self.context['path-handler'].Parse(
        'targetPools', args.name, region=args.region)

    if args.instances:
      instances = []
      for instance in args.instances:
        instances.append(self.context['path-handler'].Normalize(
            'instances', instance))

    else:
      target_pool = self.GetTargetPool(target_pool_context)
      instances = target_pool.instances

    # If the target pool has no instances, we should return an empty
    # list.
    if not instances:
      return []

    requests = []
    for instance in instances:
      request_message = messages.ComputeTargetPoolsGetHealthRequest(
          instanceReference=messages.InstanceReference(
              instance=instance),
          project=target_pool_context['project'],
          region=target_pool_context['region'],
          targetPool=target_pool_context['targetPool'])
      requests.append((self.service, 'GetHealth', request_message))

    return request_helper.MakeRequests(
        requests=requests,
        http=self.context['http'],
        batch_url=self.context['batch-url'])


GetHealth.detailed_help = {
    'brief': 'Get the health of instances in a target pool',
    'DESCRIPTION': """\
        *{command}* displays the health of instances in a target pool.
        """,
}

