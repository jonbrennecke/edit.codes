# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for attaching a disk to an instance."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import resolvers


MODE_OPTIONS = ['ro', 'rw']


class AttachDisk(base_classes.BaseAsyncMutator):
  """Attaches a disk to an instance."""

  @staticmethod
  def Args(parser):
    instance_name = parser.add_argument(
        'name',
        metavar='INSTANCE',
        help='The name of the instance to attach the disk to.')
    instance_name.detailed_help = """\
        The name of, or a fully- or partially-qualified path to the
        instance to which the disk should be attached. Using a path
        containing the zone will render the --zone flag optional. For
        example, providing ``us-central2-a/instances/my-instance''
        is equivalent to providing ``my-instance'' with
        ``--zone us-central2-a''.
        """

    parser.add_argument(
        '--device-name',
        help=('An optional name that indicates the disk name the guest '
              'operating system will see.'))

    disk = parser.add_argument(
        '--disk',
        help='The name of the disk to attach to the instance.',
        required=True)
    disk.detailed_help = """\
        The name of, or a fully- or partially-qualified path to the
        disk to attach to the instance. Using a path
        containing the zone will render the --zone flag optional. For
        example, providing ``us-central2-a/instances/my-disk''
        is equivalent to providing ``my-disk'' with
        ``--zone us-central2-a''.
        """

    mode = parser.add_argument(
        '--mode',
        choices=MODE_OPTIONS,
        default='rw',
        help='Specifies the mode of the disk.')
    mode.detailed_help = """\
        Specifies the mode of the disk. Supported options are ``ro'' for
        read-only and ``rw'' for read-write. If omitted, ``rw'' is used as
        a default. It is an error to attach a disk in read-write mode to
        more than one instance.
        """

    parser.add_argument(
        '--zone',
        help='The zone in which the instance and disk reside.')

  @property
  def service(self):
    return self.context['compute'].instances

  @property
  def method(self):
    return 'AttachDisk'

  @property
  def print_resource_type(self):
    return 'instances'

  def RegisterCustomResolvers(self):
    self.context['path-handler'].RegisterResolver(
        'instances', 'zone', resolvers.GetZoneFromArgumentsOrDisk)
    self.context['path-handler'].RegisterResolver(
        'disks', 'zone', resolvers.GetZoneFromArgumentsOrInstance)

  def CreateRequests(self, args):
    """Returns a request for attaching a disk to an instance."""
    self.RegisterCustomResolvers()

    instance_context = self.context['path-handler'].Parse(
        'instances', args.name, zone=args.zone, related_disk=args.disk)

    if args.mode == 'rw':
      mode = messages.AttachedDisk.ModeValueValuesEnum.READ_WRITE
    else:
      mode = messages.AttachedDisk.ModeValueValuesEnum.READ_ONLY

    request = messages.ComputeInstancesAttachDiskRequest(
        instance=instance_context['instance'],
        project=instance_context['project'],
        attachedDisk=messages.AttachedDisk(
            deviceName=args.device_name,
            mode=mode,
            source=self.context['path-handler'].Normalize(
                'disks', args.disk, zone=args.zone, related_instance=args.name),
            type=messages.AttachedDisk.TypeValueValuesEnum.PERSISTENT),
        zone=instance_context['zone'])

    return [request]


AttachDisk.detailed_help = {
    'brief': ('Attach a disk to an instance'),
    'DESCRIPTION': """\
        *{command}* is used to attach a disk to an instance. For example,

          $ compute instances attach-disk my-instance --disk my-disk
            --zone us-central1-a

        attaches the disk named ``my-disk'' to the instance named
        ``my-instance'' in zone ``us-central1-a''.
        """,
}

