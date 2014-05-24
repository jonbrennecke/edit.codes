# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing networks."""
from googlecloudsdk.compute.lib import base_classes


class ListNetworks(base_classes.GlobalLister):
  """List Google Compute Engine networks."""

  @property
  def service(self):
    return self.context['compute'].networks

  @property
  def print_resource_type(self):
    return 'networks'


ListNetworks.detailed_help = {
    'brief': 'List Google Compute Engine networks',
    'DESCRIPTION': """\
       *{command}* lists the URIs of Google Compute Engine networks in
       a project. The ``-l'' option can be used to display summary
       data such as the networks' range and gateway.
       """,
}
