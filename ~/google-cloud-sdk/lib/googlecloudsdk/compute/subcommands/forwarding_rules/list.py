# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing forwarding rules."""
from googlecloudsdk.compute.lib import base_classes


class ListForwardingRules(base_classes.RegionalLister):
  """List forwarding rules."""

  @property
  def service(self):
    return self.context['compute'].forwardingRules

  @property
  def print_resource_type(self):
    return 'forwardingRules'


ListForwardingRules.detailed_help = {
    'brief': 'List forwarding rules',
    'DESCRIPTION': """\
        *{command}* lists the URIs of Google Compute Engine forwarding
        rules in a project. The ``-l'' option can be used to display
        summary data such as the target and the IP addresss and
        protocol. Users who want to see more data should use 'gcloud
        compute forwarding-rules get'.

        By default, forwarding rules from all regions are listed. The
        results can be narrowed down by providing ``--region''.
        """,
}
