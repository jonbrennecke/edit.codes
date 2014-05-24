# Copyright 2014 Google Inc. All Rights Reserved.

"""Implements the command for SSHing into an instance."""

import getpass
import logging
import subprocess

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import ssh_utils


class SSH(ssh_utils.BaseSSHCommandForClientsWithOpenSSHSupport):
  """SSH into a virtual machine instance."""

  @staticmethod
  def Args(parser):
    ssh_utils.BaseSSHCommandForClientsWithOpenSSHSupport.Args(parser)

    user_host = parser.add_argument(
        'user_host',
        help='Specifies the instance to SSH into.',
        metavar='[USER@]INSTANCE')
    user_host.detailed_help = """\
        Specifies the instance to SSH into. If ``INSTANCE'' is the
        name of the instance, the ``--zone'' flag must be
        specified. If ``INSTANCE'' is a suffix of the instance's URI
        that contains the zone (e.g.,
        ``us-central2-a/instances/my-instance''), then ``--zone'' can
        be omitted.
        +
        ``USER'' specifies the username with which to SSH. If omitted,
        $USER from the environment is selected.
        """

    parser.add_argument(
        '--command',
        help='A command to run on the virtual machine.')

    parser.add_argument(
        '--zone',
        help='The zone of the instance.')

  def Run(self, args):
    super(SSH, self).Run(args)
    self.EnsureSSHKeyIsInProject()

    parts = args.user_host.split('@')
    if len(parts) == 1:
      user = getpass.getuser()
      instance = parts[0]
    elif len(parts) == 2:
      user, instance = parts
    else:
      raise exceptions.ToolException(
          'expected argument of the form [USER@]INSTANCE; received: {0}'
          .format(args.user_host))

    instance_context = self.context['path-handler'].Parse(
        'instances', instance, zone=args.zone)
    instance_resource = self.GetInstances([instance_context])[0]
    external_ip_address = ssh_utils.GetExternalIPAddress(instance_resource)

    ssh_args = [
        self.ssh_executable,
        '-i', self.ssh_key_file,
        user + '@' + external_ip_address,
    ]
    if args.command:
      ssh_args.append('--')
      ssh_args.append(args.command)

    logging.debug('ssh command: %s', ' '.join(ssh_args))
    subprocess.check_call(ssh_args)


SSH.detailed_help = {
    'brief': 'SSH into a virtual machine instance',
    'DESCRIPTION': """\
        *{command}* is a thin wrapper around the 'ssh' command that
        takes care of authentication and the translation of the
        instance name into an IP address.

        This command ensures that the user's public SSH key is present
        in the project's metadata. If the user does not have a public
        SSH key, one is generated using 'ssh-keygen'.
        """,
    'EXAMPLES': """\
        To SSH into ``my-instance'' in zone ``us-central2-a'', run:

          $ {command} my-instance --zone us-central2-a

        You can omit the ``--zone'' flag if the zone is provided in
        the positional argument:

          $ {command} us-central2-a/instances/my-instance

        You can also run a command on the virtual machine. For
        example, to get a snapshot of the guest's process tree, run:

          $ {command} my-instance --zone us-central2-a --command "ps -ejH"
        """,
}
