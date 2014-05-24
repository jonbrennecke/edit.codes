# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing target pools."""
from googlecloudsdk.compute.lib import base_classes


class ListTargetPools(base_classes.RegionalLister):
  """List target pools."""

  @property
  def service(self):
    return self.context['compute'].targetPools

  @property
  def print_resource_type(self):
    return 'targetPools'


ListTargetPools.detailed_help = {
    'brief': 'List Google Compute Engine target pools',
    'DESCRIPTION': """\
        *{command}* lists the URIs of Google Compute Engine target
        pools in a project. The ``-l'' option can be used to
        display summary data such as the backup pool or
        session affinity for each target pool. Users who want to see more data
        should use 'gcloud compute target-pools get'.

        By default, target pools from all regions are listed. The results can
        be narrowed down by providing ``--region''.
        """,
}
