# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing routes."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List routes."""

  @property
  def service(self):
    return self.context['compute'].routes

  @property
  def print_resource_type(self):
    return 'routes'


List.detailed_help = {
    'brief': 'List routes.',
    'DESCRIPTION': """\
        *{command}* lists the URIs of Google Compute Engine routes in
        a project. The ``-l'' option can be used to display summary
        data such as the routes' network, destination range, and next
        hop instance. Users who want to see more data should use
        'gcloud compute routes get'.
        """,
}
