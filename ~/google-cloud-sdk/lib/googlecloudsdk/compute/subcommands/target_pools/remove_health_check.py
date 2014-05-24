# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for removing health checks from target pools."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes


class RemoveHealthCheck(base_classes.BaseAsyncMutator):
  """Remove a health check from a target pool."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--health-check',
        help=('Specifies an HTTP health check object to remove from the '
              'target pool.'),
        metavar='HEALTH_CHECK',
        required=True)

    parser.add_argument(
        '--region',
        help='The region of the target pool.')

    parser.add_argument(
        'name',
        help=('The name of the target pool from which to remove the '
              'health check.'))

  @property
  def service(self):
    return self.context['compute'].targetPools

  @property
  def method(self):
    return 'RemoveHealthCheck'

  @property
  def print_resource_type(self):
    return 'targetPools'

  def CreateRequests(self, args):
    target_pool_context = self.context['path-handler'].Parse(
        'targetPools', args.name, region=args.region)

    health_check = self.context['path-handler'].Normalize(
        'httpHealthChecks', args.health_check)

    request = messages.ComputeTargetPoolsRemoveHealthCheckRequest(
        region=target_pool_context['region'],
        project=target_pool_context['project'],
        targetPool=target_pool_context['targetPool'],
        targetPoolsRemoveHealthCheckRequest=(
            messages.TargetPoolsRemoveHealthCheckRequest(
                healthChecks=[messages.HealthCheckReference(
                    healthCheck=health_check)])))

    return [request]


RemoveHealthCheck.detailed_help = {
    'brief': 'Remove an HTTP health check from a target pool',
    'DESCRIPTION': """\
        *{command}* is used to remove an HTTP health check
        from a target pool. Health checks are used to determine
        the health status of instances in the target pool. For more
        information on health checks and load balancing, see
        link:https://developers.google.com/compute/docs/load-balancing/[].
        """,
}

