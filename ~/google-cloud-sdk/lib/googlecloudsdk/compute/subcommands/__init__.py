# Copyright 2014 Google Inc. All Rights Reserved.
"""The super-group for the compute CLI."""

import urlparse

from googlecloudapis.compute.v1 import compute_v1_client
from googlecloudsdk.calliope import base
from googlecloudsdk.compute.lib import api_context_parser
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import resolvers
from googlecloudsdk.core import cli
from googlecloudsdk.core import properties


def _RegisterDefaultPathResolvers(path_handler):
  path_handler.RegisterDefaultResolver(
      'project', resolvers.GetDefaultProject)
  path_handler.RegisterDefaultResolver(
      'region', resolvers.GetRegionFromArguments)
  path_handler.RegisterDefaultResolver(
      'zone', resolvers.GetZoneFromArguments)


class Compute(base.Group):
  """Read and manipulate Google Compute Engine resources."""

  def Filter(self, context, _):
    http = cli.Http()
    context['http'] = http

    api_host = properties.VALUES.core.api_host.Get()
    compute_url = urlparse.urljoin(api_host, 'compute/v1/')
    context['batch-url'] = urlparse.urljoin(api_host, 'batch')

    v1_path_handler = api_context_parser.ApiContextParser(
        compute_url, constants.COMPUTE_V1_API_CONTEXT)
    _RegisterDefaultPathResolvers(v1_path_handler)
    context['path-handler'] = v1_path_handler

    v1_compute = compute_v1_client.ComputeV1(
        url=compute_url,
        get_credentials=False,
        http=http)
    context['compute'] = v1_compute


Compute.detailed_help = {
    'brief': 'Read and manipulate Google Compute Engine resources',
}

