# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for setting whether to auto-delete a disk."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import resolvers


class SetDiskAutoDelete(base_classes.ReadSetCommand):
  """Set auto-delete behavior for disks."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--zone',
        help='The zone of the instance.')

    instance_name = parser.add_argument(
        'name',
        metavar='INSTANCE',
        help=('The name of, or a fully- or partially-qualified path to the '
              'instance for which to set disk auto-deletion.'))
    instance_name.detailed_help = """\
        The name of, or a fully- or partially-qualified path to the
        instance for which to set disk auto-deletion. Using a path
        containing the zone will render the --zone flag optional. For
        example, providing ``us-central2-a/instances/my-instance''
        is equivalent to providing ``my-instance'' with
        ``--zone us-central2-a''.
        """

    auto_delete_group = parser.add_mutually_exclusive_group(required=True)

    auto_delete_group.add_argument(
        '--auto-delete',
        action='store_true',
        help='Set auto-delete for the given disk to true.')

    auto_delete_group.add_argument(
        '--no-auto-delete',
        action='store_true',
        help='Set auto-delete for the given disk to false.')

    disk_group = parser.add_mutually_exclusive_group(required=True)

    disk = disk_group.add_argument(
        '--disk',
        help=('Specify a disk to set auto-delete for by persistent disk '
              'name.'))
    disk.detailed_help = """\
        Specifies a disk to set auto-delete for by its resource name. If
        you specify a disk to set auto-delete for by persistent disk name,
        then you must not specify its device name using the
        ``--device-name'' flag.
        """

    device_name = disk_group.add_argument(
        '--device-name',
        help=('Specify a disk to set auto-delete for by the name the '
              'guest operating system sees.'))
    device_name.detailed_help = """\
        Specifies a disk to set auto-delete for by its device name,
        which is the name that the guest operating system sees. The
        device name is set at the time that the disk is attached to the
        instance, and need not be the same as the persistent disk name.
        If the disk's device name is specified, then its persistent disk
        name must not be specified using the ``--disk'' flag.
        """

  @property
  def service(self):
    return self.context['compute'].instances

  @property
  def method(self):
    return 'SetDiskAutoDelete'

  @property
  def print_resource_type(self):
    return 'instances'

  def Run(self, args):
    self.RegisterCustomResolvers()
    return super(SetDiskAutoDelete, self).Run(args)

  def RegisterCustomResolvers(self):
    self.context['path-handler'].RegisterResolver(
        'instances', 'zone', resolvers.GetZoneFromArgumentsOrDisk)
    self.context['path-handler'].RegisterResolver(
        'disks', 'zone', resolvers.GetZoneFromArgumentsOrInstance)

  def GetContext(self, args):
    return self.context['path-handler'].Parse(
        'instances', args.name, zone=args.zone, related_disk=args.disk)

  def GetGetRequest(self, args):
    return (self.service,
            'Get',
            messages.ComputeInstancesGetRequest(
                instance=self.resource_context['instance'],
                project=self.resource_context['project'],
                zone=self.resource_context['zone']))

  def GetSetRequest(self, args, existing):
    device_name = None
    if args.disk:
      disk_uri = self.context['path-handler'].Normalize(
          'disks', args.disk, zone=args.zone, related_instance=args.name)
      for disk in existing.disks:
        if disk.source == disk_uri:
          device_name = disk.deviceName
      if device_name is None:
        raise exceptions.ToolException(
            'disk "{0}" is not attached to instance "{1}"'.format(
                args.disk, self.resource_context['instance']))

    else:
      for disk in existing.disks:
        if disk.deviceName == args.device_name:
          device_name = disk.deviceName
      if device_name is None:
        raise exceptions.ToolException(
            'no disk with device name "{0}" is attached to instance "{1}"'
            .format(args.device_name, self.resource_context['instance']))

    return (self.service,
            'SetDiskAutoDelete',
            messages.ComputeInstancesSetDiskAutoDeleteRequest(
                deviceName=device_name,
                instance=self.resource_context['instance'],
                project=self.resource_context['project'],
                zone=self.resource_context['zone'],
                autoDelete=True if args.auto_delete else False))


SetDiskAutoDelete.detailed_help = {
    'brief': 'Set auto-delete behavior for disks',
    'DESCRIPTION': """\
        *${command}* is used to configure the auto-delete behavior for disks
        attached to Google Compute Engine virtual machines. When
        auto-delete is on, the persistent disk is deleted when the
        instance it is attached to is deleted.
        """,
}

