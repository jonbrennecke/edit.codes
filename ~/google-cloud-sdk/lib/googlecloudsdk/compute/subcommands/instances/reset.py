# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for resetting an instance."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes


class Reset(base_classes.BaseAsyncMutator):
  """Reset a virtual machine instance."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--zone',
        help='Specifies the zone of the instance.')
    parser.add_argument(
        'name',
        help='The name of the instance to reset.')

  @property
  def service(self):
    return self.context['compute'].instances

  @property
  def method(self):
    return 'Reset'

  @property
  def print_resource_type(self):
    return 'instances'

  def CreateRequests(self, args):
    instance_context = self.context['path-handler'].Parse(
        'instances', args.name, zone=args.zone)

    request = messages.ComputeInstancesResetRequest(
        instance=instance_context['instance'],
        project=instance_context['project'],
        zone=instance_context['zone'])
    return [request]


Reset.detailed_help = {
    'brief': 'Reset a virtual machine instance',
    'DESCRIPTION': """\
        *{command}* is used to perform a hard reset on a Google
        Compute Engine virtual machine.
        """,
}

