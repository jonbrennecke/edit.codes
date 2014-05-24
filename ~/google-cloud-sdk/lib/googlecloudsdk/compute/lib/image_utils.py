# Copyright 2014 Google Inc. All Rights Reserved.
"""Common classes and functions for images."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import lister
from googlecloudsdk.core import properties


class ImageResourceFetcher(object):
  """Mixin class for displaying images."""

  def GetResources(self, args, errors):
    """Yields images from (potentially) multiple projects."""
    filter_expression = lister.ConstructNameFilterExpression(args.name_regex)

    requests = [
        messages.ComputeImagesListRequest(
            filter=filter_expression,
            maxResults=constants.MAX_RESULTS_PER_PAGE,
            project=properties.VALUES.core.project.Get(required=True)),
    ]

    if not args.no_standard_images:
      for project in constants.IMAGE_PROJECTS:
        requests.append(messages.ComputeImagesListRequest(
            filter=filter_expression,
            maxResults=constants.MAX_RESULTS_PER_PAGE,
            project=project))

    images = lister.BatchList(
        service=self.service,
        requests=requests,
        http=self.context['http'],
        batch_url=self.context['batch-url'],
        errors=errors)

    for image in images:
      if not image.deprecated or args.show_deprecated:
        yield image


def AddImageFetchingArgs(parser):
  """Adds common flags for getting and listing images."""
  parser.add_argument(
      '--show-deprecated',
      action='store_true',
      help='If provided, deprecated images are shown.')

  no_standard_images = parser.add_argument(
      '--no-standard-images',
      action='store_true',
      help='If provided, images from well-known image projects are not shown.')
  no_standard_images.detailed_help = """\
     If provided, images from well-known image projects are not
     shown. The well known image projects are: {0}.
     """.format(', '.join(constants.IMAGE_PROJECTS))

