# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for creating instances."""
import collections

from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import metadata_utils

DISK_METAVAR = (
    'name=NAME [mode={ro,rw}] [boot={yes,no}] [device-name=DEVICE_NAME]')

MIGRATION_OPTIONS = sorted(
    messages.Scheduling.OnHostMaintenanceValueValuesEnum.to_dict().keys())


class CreateInstances(base_classes.BaseAsyncMutator):
  """Create Google Compute Engine virtual machine instances."""

  @staticmethod
  def Args(parser):
    metadata_utils.AddMetadataArgs(parser)

    boot_disk_device_name = parser.add_argument(
        '--boot-disk-device-name',
        help='The name the guest operating system will see the boot disk as.')
    boot_disk_device_name.detailed_help = """\
        The name the guest operating system will see for the boot disk
        as. This option can only be specified when using
        ``--image''. When creating more than one instance, the value
        of the device name will apply to all of the instances' boot
        disks.
        """

    def AddImageHelp():
      return """\
          Specifies the boot image for the instances. For each instance,
          a new boot disk will be created from the given image. Each
          boot disk will have the same name as the instance. The value
          for this option can be the name of an image in the current
          project or a partially-qualified resource path that references
          an image in another project. For example,
          ``projects/google/images/bunny'' will select the ``bunny''
          image that resides in the ``google'' project. When crossing
          project boundaries, the referenced resource must be visible to
          the current project.
          +
          To get a list of available images, run 'gcloud compute images list -l'.
          +
          When using this option, ``--boot-disk-device-name'' and
          ``--boot-disk-size'' can be used to override the boot disk's
          device name and size, respectively.
          +
          For convenience, the following aliases are available for
          commonly-used images:
          +
          [options="header",format="csv",grid="none",frame="none"]
          |========
          Alias,URI
          {aliases}
          |========
          +
          As new images are released, these aliases will be updated. If
          using this tool in a script where depending on a specific
          version of an image is necessary, then do not use the
          aliases. Instead, use a direct reference to the image.
          +
          Aliases are expanded first, so avoid creating images in
          your project whose names are in the set of aliases. If you
          do create an image whose name matches an alias, you can
          refer to it by using a partially-qualified URI (e.g.,
          ``my-project/global/images/debian-7'').
          +
          By default, ``{default_image}'' is assumed for this flag.
          """.format(
              default_image=constants.DEFAULT_IMAGE,
              aliases='\n          '.join(
                  ','.join(value) for value in
                  sorted(constants.IMAGE_ALIASES.iteritems())))

    image = parser.add_argument(
        '--image',
        help='The image that the boot disk will be initialized with.')
    image.detailed_help = AddImageHelp

    parser.add_argument(
        '--can-ip-forward',
        action='store_true',
        help=('If provided, allows the instances to send and receive packets '
              'with non-matching destination or source IP addresses.'))

    parser.add_argument(
        '--description',
        help='Specifies a textual description of the instances.')

    disk = parser.add_argument(
        '--disk',
        action=arg_parsers.AssociativeList(spec={
            'name': str,
            'mode': str,
            'boot': str,
            'device-name': str,
        }, append=True),
        help='Attaches persistent disks to the instances.',
        metavar='PROPERTY=VALUE',
        nargs='+')
    disk.detailed_help = """
        Attaches persistent disks to the instances. The disks
        specified must already exist.

        *name*::: The disk to attach to the instances. When creating
        more than one instance and using this property, the only valid
        mode for attaching the disk is read-only (see *mode* below).

        *mode*::: Specifies the mode of the disk. Supported options
        are ``ro'' for read-only and ``rw'' for read-write. If
        omitted, ``rw'' is used as a default. It is an error for mode
        to be ``rw'' when creating more than one instance because
        read-write disks can only be attached to a single instance.

        *boot*::: If ``yes'', indicates that this is a boot disk. The
        virtual machines will use the first partition of the disk for
        their root file systems. The default value for this is ``no''.

        *device-name*::: An optional name that indicates the disk name
        the guest operating system will see. If omitted, a device name
        of the form ``persistent-disk-N'' will be used.
        """

    addresses = parser.add_mutually_exclusive_group()
    addresses.add_argument(
        '--no-address',
        action='store_true',
        help=('If provided, the instances will not be assigned external IP '
              'addresses.'))
    address = addresses.add_argument(
        '--address',
        help='Assigns the given external IP address to an instance.')
    address.detailed_help = """\
        Assigns the given external IP address to an instance. This
        option can only be used when creating a single instance.
        """

    machine_type = parser.add_argument(
        '--machine-type',
        help='Specifies the machine type used for the instances.',
        default=constants.DEFAULT_MACHINE_TYPE)
    machine_type.detailed_help = """\
        Specifies the machine type used for the instances. To get a
        list of available machine types, run 'gcloud compute
        machine-types list'.
        """

    maintenance_policy = parser.add_argument(
        '--maintenance-policy',
        choices=MIGRATION_OPTIONS,
        default='MIGRATE',
        help=('Specifies the behavior of the instances when their host '
              'machines undergo maintenance.'))
    maintenance_policy.detailed_help = """\
        Specifies the behavior of the instances when their host machines undergo
        maintenance. ``TERMINATE'' indicates that the instances should be
        terminated. ``MIGRATE'' indicates that the instances should be
        migrated to a new host. Choosing ``MIGRATE'' will temporarily impact the
        performance of instances during a migration event.
        """

    network = parser.add_argument(
        '--network',
        default=constants.DEFAULT_NETWORK,
        help='Specifies the network that the instances will be part of.')
    network.detailed_help = """\
        Specifies the network that the instances will be part of. If
        omitted, the ``default'' network is used.
        """

    restart_on_failure = parser.add_argument(
        '--restart-on-failure',
        action='store_true',
        default=False,
        help=('If provided, the instances are restarted if they are terminated '
              'by Compute Engine'))
    restart_on_failure.detailed_help = """\
        If provided, the instances will be restarted automatically if
        they are terminated by Compute Engine. If not provided, failed
        instances will not be restarted. This does not affect
        terminations performed by the user.
    """

    scopes_group = parser.add_mutually_exclusive_group()

    def AddScopesHelp():
      return """\
          Specifies service accounts and scopes for the
          instances. Service accounts generate access tokens that can be
          accessed through the instance metadata server and used to
          authenticate applications on the instance. The account can be
          either an email address or an alias corresponding to a
          service account. If account is omitted, the project's default
          service account is used. The default service account can be
          specified explicitly by using the alias ``default''. Example:

            $ {{command}} my-instance \\
                --scopes compute-rw me@project.gserviceaccount.com=storage-rw
          +
          If this flag is not provided, the ``storage-ro'' scope is
          added to the instances. To create instances with no scopes,
          use ``--no-scopes'':

            $ {{command}} my-instance --no-scopes
          +
          SCOPE can be either the full URI of the scope or an
          alias. Available aliases are:
          +
          [options="header",format="csv",grid="none",frame="none"]
          |========
          Alias,URI
          {aliases}
          |========
          """.format(
              aliases='\n          '.join(
                  ','.join(value) for value in
                  sorted(constants.SCOPES.iteritems())))
    scopes = scopes_group.add_argument(
        '--scopes',
        help='Specifies service accounts and scopes for the instances.',
        metavar='[ACCOUNT=]SCOPE',
        nargs='+')
    scopes.detailed_help = AddScopesHelp

    scopes_group.add_argument(
        '--no-scopes',
        action='store_true',
        help=('If provided, the default scopes ({scopes}) are not added to the '
              'instances.'.format(scopes=', '.join(constants.DEFAULT_SCOPES))))

    tags = parser.add_argument(
        '--tags',
        help='A list of tags to apply to the instances.',
        metavar='TAG',
        nargs='+')
    tags.detailed_help = """\
        Specifies a list of tags to apply to the instances for
        identifying the instances to which network firewall rules will
        apply. See *gcloud-compute-firewalls-create(1)* for more
        details.
        """

    parser.add_argument(
        'names',
        metavar='NAME',
        nargs='+',
        help='The names of the instances to create.')

    parser.add_argument(
        '--zone',
        help='The zone to create the instances in.')

  @property
  def service(self):
    return self.context['compute'].instances

  @property
  def method(self):
    return 'Insert'

  @property
  def print_resource_type(self):
    return 'instances'

  def CreateAttachedDiskMessages(self, args, instance_context):
    """Returns a list of AttachedDisk messages based on command-line args."""
    disks = []
    boot_disk = None

    for disk in args.disk or []:
      if 'name' not in disk:
        raise exceptions.ToolException(
            'missing name in --disk; --disk value must be of the form "{0}"'
            .format(DISK_METAVAR))
      name = disk['name']

      # Resolves the mode.
      mode_value = disk.get('mode', 'ro')
      if mode_value == 'rw':
        mode = messages.AttachedDisk.ModeValueValuesEnum.READ_WRITE
      elif mode_value == 'ro':
        mode = messages.AttachedDisk.ModeValueValuesEnum.READ_ONLY
      else:
        raise exceptions.ToolException(
            'value for mode in --disk must be "rw" or "ro"; received: {0}'
            .format(mode_value))

      # Ensures that the user is not trying to attach a read-write
      # disk to more than one instance.
      if len(args.names) > 1 and mode_value == 'rw':
        raise exceptions.ToolException(
            'cannot attach disk "{0}" in read-write mode to more than one '
            'instance'.format(name))

      # Resolves the boot flag.
      boot_value = disk.get('boot', 'no')
      if boot_value not in ['yes', 'no']:
        raise exceptions.ToolException(
            'value for boot in --disk must be "yes" or "no"; received: {0}'
            .format(boot_value))
      boot = boot_value == 'yes'

      attached_disk = messages.AttachedDisk(
          boot=boot,
          deviceName=disk.get('device-name'),
          mode=mode,
          source=self.context['path-handler'].Normalize(
              'disks', name, zone=instance_context['zone']),
          type=messages.AttachedDisk.TypeValueValuesEnum.PERSISTENT)

      # If this is a boot disk and we have already seen a boot disk,
      # we need to fail because only one boot disk can be attached.
      if boot and boot_disk:
        raise exceptions.ToolException(
            'each instance can have exactly one boot disk; at least two '
            'boot disks were specified through --disk')

      # The boot disk must end up at index 0, so we hold on to it and
      # prepend it to the list at the end.
      if boot:
        boot_disk = attached_disk
      else:
        disks.append(attached_disk)

    # We have gone through the --disk values.

    if args.image and boot_disk:
      raise exceptions.ToolException(
          'each instance can have exactly one boot disk; one boot disk '
          'was specified through --disk and another through --image')

    if not boot_disk:
      image = constants.IMAGE_ALIASES.get(
          args.image or constants.DEFAULT_IMAGE, args.image)
      boot_disk = messages.AttachedDisk(
          autoDelete=True,
          boot=True,
          deviceName=args.boot_disk_device_name,
          initializeParams=messages.AttachedDiskInitializeParams(
              sourceImage=self.context['path-handler'].Normalize(
                  'images', image)),
          mode=messages.AttachedDisk.ModeValueValuesEnum.READ_WRITE,
          type=messages.AttachedDisk.TypeValueValuesEnum.PERSISTENT)

    return [boot_disk] + disks

  def CreateServiceAccountMessages(self, args):
    """Returns a list of ServiceAccount messages corresponding to --scopes."""
    if args.no_scopes:
      scopes = []
    else:
      scopes = args.scopes or constants.DEFAULT_SCOPES

    accounts_to_scopes = collections.defaultdict(list)
    for scope in scopes:
      parts = scope.split('=')
      if len(parts) == 1:
        account = 'default'
        scope_uri = scope
      elif len(parts) == 2:
        account, scope_uri = parts
      else:
        raise exceptions.ToolException(
            '--scopes values must be of the form [ACCOUNT=]SCOPE; received: {0}'
            .format(scope))

      # Expands the scope if the user provided an alias like
      # "compute-rw".
      scope_uri = constants.SCOPES.get(scope_uri, scope_uri)

      accounts_to_scopes[account].append(scope_uri)

    res = []
    for account, scopes in sorted(accounts_to_scopes.iteritems()):
      res.append(messages.ServiceAccount(
          email=account,
          scopes=sorted(scopes)))
    return res

  def CreateRequests(self, args):
    requests = []
    for name in args.names:
      instance_context = self.context['path-handler'].Parse(
          'instances', name, zone=args.zone)

      # Handles the machine type.
      machine_type = self.context['path-handler'].Normalize(
          'machineTypes', args.machine_type, zone=instance_context['zone'])

      # Handles networking-related configs.
      if args.no_address:
        access_configs = [
            messages.AccessConfig(
                name=constants.DEFAULT_ACCESS_CONFIG_NAME,
                type=messages.AccessConfig.TypeValueValuesEnum.ONE_TO_ONE_NAT)
            ]
      else:
        access_config = messages.AccessConfig(
            name=constants.DEFAULT_ACCESS_CONFIG_NAME,
            type=messages.AccessConfig.TypeValueValuesEnum.ONE_TO_ONE_NAT)

        # If the user provided an external IP, populate the access
        # config with it.
        if args.address:
          access_config.natIP = args.address

        access_configs = [access_config]

      network_interfaces = [messages.NetworkInterface(
          accessConfigs=access_configs,
          network=self.context['path-handler'].Normalize(
              'networks', args.network))]

      # Handles metadata.
      metadata = metadata_utils.ConstructMetadataMessage(
          metadata=args.metadata, metadata_from_file=args.metadata_from_file)

      if args.tags:
        tags = messages.Tags(items=args.tags)
      else:
        tags = None

      requests.append(messages.ComputeInstancesInsertRequest(
          instance=messages.Instance(
              canIpForward=args.can_ip_forward,

              # Note that each instance can end up in a different
              # zone, so we have to create the AttachedDisk messages
              # for each instance individually.
              disks=self.CreateAttachedDiskMessages(args, instance_context),

              description=args.description,
              machineType=machine_type,
              metadata=metadata,
              name=instance_context['instance'],
              networkInterfaces=network_interfaces,
              serviceAccounts=self.CreateServiceAccountMessages(args),
              scheduling=messages.Scheduling(
                  automaticRestart=args.restart_on_failure,
                  onHostMaintenance=(
                      messages.Scheduling.OnHostMaintenanceValueValuesEnum(
                          args.maintenance_policy))),
              tags=tags,
          ),
          project=instance_context['project'],
          zone=instance_context['zone']))

    return requests


CreateInstances.detailed_help = {
    'brief': 'Create Compute Engine virtual machine instances',
    'DESCRIPTION': """\
        *{command}* facilitates the creation of Google Compute Engine
        virtual machines. Virtual machines can be created in many
        ways. For example, running:

          $ {command} my-instance-1 my-instance-2 my-instance-3

        will create three instances called ``my-instance-1'',
        ``my-instance-2'', and ``my-instance-3''.

        For more examples, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To create an instance with the latest ``Red Hat Enterprise Linux
        6'' image available, run:

          $ {command} my-instance --image rhel-6
        """,
}

