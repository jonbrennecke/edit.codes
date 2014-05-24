# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting forwarding rules."""
from googlecloudsdk.compute.lib import base_classes


class DeleteForwardingRules(base_classes.RegionalDeleter):
  """Delete forwarding rules."""

  @property
  def service(self):
    return self.context['compute'].forwardingRules

  @property
  def collection(self):
    return 'forwardingRules'


DeleteForwardingRules.detailed_help = {
    'brief': 'Delete forwarding rules',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine forwarding
         rules.
        """,
}
