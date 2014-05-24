# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for setting scheduling for virtual machine instances."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes

MIGRATION_OPTIONS = sorted(
    messages.Scheduling.OnHostMaintenanceValueValuesEnum.to_dict().keys())


class SetSchedulingInstances(base_classes.BaseAsyncMutator):
  """Set scheduling options for Google Compute Engine virtual machine instances.
  """

  @staticmethod
  def Args(parser):
    restart_group = parser.add_mutually_exclusive_group()

    restart_on_failure = restart_group.add_argument(
        '--restart-on-failure',
        action='store_true',
        help='If true, the instance will be restarted on failure.')
    restart_on_failure.detailed_help = """\
        If provided, the instances will be restarted automatically if they
        are terminated by the system. This flag is mutually exclusive with
        ``--no-restart-on-failure''. This does not affect terminations
        performed by the user.
        """

    no_restart_on_failure = restart_group.add_argument(
        '--no-restart-on-failure',
        action='store_true',
        help='If true, the instance will be restarted on failure.')
    no_restart_on_failure.detailed_help = """\
        If provided, the instances will not be restarted automatically if they
        are terminated by the system. Mutually exclusive with
        --restart-on-failure. This does not affect terminations performed by the
        user.
        """

    maintenance_policy = parser.add_argument(
        '--maintenance-policy',
        choices=MIGRATION_OPTIONS,
        help=('Specifies the behavior of the instances when their host '
              'machines undergo maintenance.'))
    maintenance_policy.detailed_help = """\
        Specifies the behavior of the instances when their host machines undergo
        maintenance. TERMINATE indicates that the instances should be
        terminated. MIGRATE indicates that the instances should be migrated to a
        new host. Choosing MIGRATE will temporarily impact the performance of
        instances during a migration event.
        """

    instance_name = parser.add_argument(
        'name',
        metavar='INSTANCE',
        help=('The name of, or a fully- or partially-qualified path to the '
              'instance for which to set scheduling options.'))
    instance_name.detailed_help = """\
        The name of, or a fully- or partially-qualified path to the
        instance for which to set scheduling options. Using a path
        containing the zone will render the --zone flag optional. For
        example, providing ``us-central2-a/instances/my-instance''
        is equivalent to providing ``my-instance'' with
        ``--zone us-central2-a''.
        """

    parser.add_argument(
        '--zone',
        help='The zone of the instance.')

  @property
  def service(self):
    return self.context['compute'].instances

  @property
  def method(self):
    return 'SetScheduling'

  @property
  def print_resource_type(self):
    return 'instances'

  def CreateRequests(self, args):
    """Returns a list of request necessary for setting scheduling options."""

    instance_context = self.context['path-handler'].Parse(
        'instances', args.name, zone=args.zone)

    scheduling_options = messages.Scheduling()

    if args.restart_on_failure:
      scheduling_options.automaticRestart = True
    elif args.no_restart_on_failure:
      scheduling_options.automaticRestart = False

    if args.maintenance_policy:
      scheduling_options.onHostMaintenance = (messages.Scheduling.
                                              OnHostMaintenanceValueValuesEnum(
                                                  args.maintenance_policy))

    request = messages.ComputeInstancesSetSchedulingRequest(
        instance=instance_context['instance'],
        project=instance_context['project'],
        scheduling=scheduling_options,
        zone=instance_context['zone'])

    return [request]


SetSchedulingInstances.detailed_help = {
    'brief': ('Set scheduling options for Google Compute Engine virtual '
              'machines'),
    'DESCRIPTION': """\
        *${command}* is used to configure scheduling options for Google Compute
        Engine virtual machines.
        """,
}

