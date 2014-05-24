# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting access configs from virtual machine instances."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants


class DeleteAccessConfig(base_classes.BaseAsyncMutator):
  """Delete access configs from Google Compute Engine virtual machines."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--zone',
        help=('The zone of the instance from which to delete the access '
              'configuration.'))

    access_config_name = parser.add_argument(
        '--access-config-name',
        default=constants.DEFAULT_ACCESS_CONFIG_NAME,
        help='Specifies the name of the access configuration to delete.')
    access_config_name.detailed_help = """\
        Specifies the name of the access configuration to delete.
        ``{0}'' is used as the default if this flag is not provided.
        """.format(constants.DEFAULT_ACCESS_CONFIG_NAME)

    parser.add_argument(
        'name',
        help="""\
            The name of, or a fully- or partially-qualified path to the
            instance from which to delete the access configuration. Using a path
            containing the zone will render the --zone flag optional. For
            example, providing ``us-central2-a/instances/my-instance''
            is equivalent to providing ``my-instance'' with
            ``--zone us-central2-a''.
            """)

    network_interface = parser.add_argument(
        '--network-interface',
        default='nic0',
        help=('Specifies the name of the network interface from which to '
              'delete the access configuration.'))
    network_interface.detailed_help = """\
        Specifies the name of the network interface from which to delete the
        access configuration. If this is not provided, then ``nic0'' is used
        as the default.
        """

  @property
  def service(self):
    return self.context['compute'].instances

  @property
  def method(self):
    return 'DeleteAccessConfig'

  @property
  def print_resource_type(self):
    return 'instances'

  def CreateRequests(self, args):
    """Returns a request necessary for removing an access config."""

    instance_context = self.context['path-handler'].Parse(
        'instances', args.name, zone=args.zone)

    request = messages.ComputeInstancesDeleteAccessConfigRequest(
        accessConfig=args.access_config_name,
        instance=instance_context['instance'],
        networkInterface=args.network_interface,
        project=instance_context['project'],
        zone=instance_context['zone'])

    return [request]


DeleteAccessConfig.detailed_help = {
    'brief': ('Delete an access configuration from the network interface of a '
              'virtual machine'),
    'DESCRIPTION': """\
        *{command}* is used to delete access configurations from network
        interfaces of Google Compute Engine virtual machines.
        """,
}

