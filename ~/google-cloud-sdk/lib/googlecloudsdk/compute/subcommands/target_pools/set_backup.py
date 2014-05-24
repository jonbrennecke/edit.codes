# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for setting a backup target pool."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.compute.lib import base_classes


class SetBackup(base_classes.BaseAsyncMutator):
  """Set a backup pool for a target pool."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--backup-pool',
        help='Name of the target pool that will serve as backup.',
        required=True)
    parser.add_argument(
        '--region',
        help='The region of the target pool.')
    parser.add_argument(
        '--failover-ratio',
        type=float,
        required=True,
        help=('The new failover ratio value for the target pool. '
              'This must be a float in the range of [0, 1].'))
    parser.add_argument(
        'name',
        help='The name of the target pool for which to set the backup pool.')

  @property
  def service(self):
    return self.context['compute'].targetPools

  @property
  def method(self):
    return 'SetBackup'

  @property
  def print_resource_type(self):
    return 'targetPools'

  def CreateRequests(self, args):
    """Returns a request necessary for setting a backup target pool."""

    target_pool_context = self.context['path-handler'].Parse(
        'targetPools', args.name, region=args.region)

    backup_pool_uri = self.context['path-handler'].Normalize(
        'targetPools', args.backup_pool,
        region=args.region)

    if args.failover_ratio is not None and (
        args.failover_ratio < 0 or args.failover_ratio > 1):
      raise calliope_exceptions.ToolException(
          '--failover-ratio must be a number between 0 and 1, inclusive')

    request = messages.ComputeTargetPoolsSetBackupRequest(
        targetPool=target_pool_context['targetPool'],
        targetReference=messages.TargetReference(
            target=backup_pool_uri,
        ),
        failoverRatio=args.failover_ratio,
        region=target_pool_context['region'],
        project=target_pool_context['project'])

    return [request]


SetBackup.detailed_help = {
    'brief': 'Set a backup pool for a target pool',
    'DESCRIPTION': """\
        *{command}* is used to set a backup target pool for a primary
        target pool, which defines the fallback behavior of the primary
        pool. If the ratio of the healthy instances in the primary pool
        is at or below the specified ``--failover-ratio value'', then traffic
        arriving at the load-balanced IP address will be directed to the
        backup pool.
        """,
}

