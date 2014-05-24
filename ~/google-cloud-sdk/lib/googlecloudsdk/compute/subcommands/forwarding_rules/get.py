# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for getting forwarding rules."""
from googlecloudsdk.compute.lib import base_classes


class GetForwardingRules(base_classes.RegionalGetter):
  """Display detailed information about forwarding rules."""

  @staticmethod
  def Args(parser):
    base_classes.RegionalGetter.Args(parser)
    base_classes.AddFieldsFlag(parser, 'forwardingRules')

  @property
  def service(self):
    return self.context['compute'].forwardingRules

  @property
  def print_resource_type(self):
    return 'forwardingRules'


GetForwardingRules.detailed_help = {
    'brief': 'Display detailed information about forwarding rules',
    'DESCRIPTION': """\
        *{command}* displays all data associated with Google Compute
        Engine forwarding rules in a project.
        """,
}
