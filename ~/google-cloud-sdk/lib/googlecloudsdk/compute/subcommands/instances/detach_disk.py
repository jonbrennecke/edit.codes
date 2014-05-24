# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for detaching a disk from an instance."""
import copy

from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import resolvers


class DetachDisk(base_classes.ReadWriteCommand):
  """Detach disks from Google Compute Engine virtual machine instances."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--zone',
        help='The zone of the instance.')

    disk_group = parser.add_mutually_exclusive_group(required=True)

    disk_name = disk_group.add_argument(
        '--disk',
        help='Specify a disk to remove by persistent disk name.')
    disk_name.detailed_help = """\
        Specifies a disk to detach by its resource name. If you specify a
        disk to remove by persistent disk name, then you must not specify its
        device name using the ``--device-name'' flag.
        """

    device_name = disk_group.add_argument(
        '--device-name',
        help=('Specify a disk to remove by the name the guest operating '
              'system sees.'))
    device_name.detailed_help = """\
        Specifies a disk to detach by its device name, which is the name
        that the guest operating system sees. The device name is set
        at the time that the disk is attached to the instance, and needs not be
        the same as the persistent disk name. If the disk's device name is
        specified, then its persistent disk name must not be specified
        using the ``--disk'' flag.
        """

    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the instance to detach the disk from.')

  @property
  def service(self):
    return self.context['compute'].instances

  @property
  def print_resource_type(self):
    return 'instances'

  def Run(self, args):
    self.RegisterCustomResolvers()
    return super(DetachDisk, self).Run(args)

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

  def GetSetRequest(self, args, replacement, existing):
    removed_disk = list(set(existing.disks) - set(replacement.disks))[0]
    return (self.service,
            'DetachDisk',
            messages.ComputeInstancesDetachDiskRequest(
                deviceName=removed_disk.deviceName,
                instance=self.resource_context['instance'],
                project=self.resource_context['project'],
                zone=self.resource_context['zone']))

  def Modify(self, args, existing):
    replacement = copy.deepcopy(existing)

    if args.disk:
      disk_uri = self.context['path-handler'].Normalize(
          'disks', args.disk, zone=args.zone, related_instance=args.name)
      replacement.disks = [disk for disk in existing.disks
                           if disk.source != disk_uri]
    else:
      replacement.disks = [disk for disk in existing.disks
                           if disk.deviceName != args.device_name]

    return replacement


DetachDisk.detailed_help = {
    'brief': 'Detach disks from Compute Engine virtual machine instances',
    'DESCRIPTION': """\
        *{command}* is used to detach disks from virtual machines.

        Detaching a disk without first unmounting it may result in
        incomplete I/O operations and data corruption.
        To unmount a persistent disk on a Linux-based image,
        ssh into the instance and run:

          $ sudo umount /dev/disk/by-id/google-DEVICE_NAME
        """,
}

