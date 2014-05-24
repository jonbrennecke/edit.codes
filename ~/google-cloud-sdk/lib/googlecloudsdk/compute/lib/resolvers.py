# Copyright 2014 Google Inc. All Rights Reserved.

"""Functions for resolving context in compute."""

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import properties


def GetZoneFromArguments(context, parser, **kwargs):
  """If the zone is not specified, use the zone flag value."""
  zone = kwargs.get('zone')
  if zone:
    zone_context = parser.Parse('zones', kwargs['zone'])
    if (zone_context['project'] !=
        properties.VALUES.core.project.Get(required=True)):
      raise exceptions.ToolException(
          'invalid project for zone: {0}; expected: {1};'.format(
              zone_context['project'],
              properties.VALUES.core.project.Get(required=True)))
    return zone_context['zone']
  else:
    raise exceptions.ToolException(
        'could not resolve zone for some resources; try specifying --zone')


def GetRegionFromArguments(context, parser, **kwargs):
  """If the region is not specified, use the region flag value."""
  region = kwargs.get('region')
  if region:
    region_context = parser.Parse('regions', kwargs['region'])
    if (region_context['project'] !=
        properties.VALUES.core.project.Get(required=True)):
      raise exceptions.ToolException(
          'invalid project for region: {0}; expected: {1};'.format(
              region_context['project'],
              properties.VALUES.core.project.Get(required=True)))
    return region_context['region']
  else:
    raise exceptions.ToolException(
        'could not resolve region for some resources; try specifying --region')


def GetDefaultProject(context, parser, **kwargs):
  """Project should typically match the default project for Cloud SDK."""
  return properties.VALUES.core.project.Get(required=True)


def RequireExplicitZone(context, parser, **kwargs):
  """If zone is not specified, fail with an actionable error."""
  if 'user_input' in kwargs:
    raise exceptions.ToolException(
        'zone must be included in the path for resource: {0}'.format(
            kwargs['user_input']))
  else:
    raise exceptions.ToolException(
        'could not resolve zone for some resources; '
        'try including the zone in the path')


# TODO(user): These GetZoneFromArgumentsOr... functions have a lot of
# redundancy. They should be consolidated in the future, when we have
# a better solution for inference.
def GetZoneFromArgumentsOrDisk(context, parser, **kwargs):
  """First try getting zone from arguments, then fall back to the disk."""
  try:
    return GetZoneFromArguments(context, parser, **kwargs)
  except exceptions.ToolException:
    related_disk = kwargs.get('related_disk')
    if related_disk:
      return parser.Parse('disks', related_disk)['zone']
    else:
      raise exceptions.ToolException(
          'could not resolve zone for some resources; try specifying --zone')


def GetZoneFromArgumentsOrInstance(context, parser, **kwargs):
  """First try getting zone from arguments, then fall back to the instance."""
  try:
    return GetZoneFromArguments(context, parser, **kwargs)
  except exceptions.ToolException:
    related_instance = kwargs.get('related_instance')
    if related_instance:
      return parser.Parse('instances', related_instance)['zone']
    else:
      raise exceptions.ToolException(
          'could not resolve zone for some resources; try specifying --zone')


def GetZoneFromArgumentsOrTargetInstance(context, parser, **kwargs):
  """First try getting zone from arguments, fall back to target instance."""
  try:
    return GetZoneFromArguments(context, parser, **kwargs)
  except exceptions.ToolException:
    related_target_instance = kwargs.get('related_target_instance')
    if related_target_instance:
      return parser.Parse('targetInstances', related_target_instance)['zone']
    else:
      raise exceptions.ToolException(
          'could not resolve zone for some resources; try specifying --zone')
