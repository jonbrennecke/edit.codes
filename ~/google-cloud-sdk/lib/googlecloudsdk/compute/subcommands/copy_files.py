# Copyright 2014 Google Inc. All Rights Reserved.

"""Implements the command for copying files from and to virtual machines."""
import logging
import subprocess

from googlecloudsdk.compute.lib import ssh_utils


class CopyFiles(ssh_utils.BaseSSHCommandForClientsWithOpenSSHSupport):
  """Copy files to and from Google Compute Engine virtual machines."""

  @staticmethod
  def Args(parser):
    ssh_utils.BaseSSHCommandForClientsWithOpenSSHSupport.Args(parser)

    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively copy entire directories.')
    parser.add_argument(
        '--zone',
        help='The zone of the instances.')
    parser.add_argument(
        'sources',
        help='Specifies a source file.',
        metavar='[[USER@]INSTANCE:]SOURCE',
        nargs='+')
    parser.add_argument(
        'destination',
        help='Specifies a destination for the source files.',
        metavar='[[USER@]INSTANCE:]DEST')

  def Run(self, args):
    super(CopyFiles, self).Run(args)

    file_specs = []
    instance_contexts = []
    instances_added = set([])

    # Creates a list of tuples where each tuple is of the form (user,
    # instance_uri, file_path). Contexts for all instances are also
    # created and saved into instance_context so we can look up their
    # external IP addresses later.
    for arg in args.sources + [args.destination]:
      # If the argument begins with "./" or "/", then we are dealing
      # with a local file that can potentially contain colons, so we
      # avoid splitting on colons. The case of remote files containing
      # colons is handled below by splitting only on the first colon.
      if arg.startswith('./') or arg.startswith('/'):
        file_specs.append((None, None, arg))
        continue

      host_file_parts = arg.split(':', 1)
      if len(host_file_parts) == 1:
        file_specs.append((None, None, host_file_parts[0]))
      else:
        user_host, file_path = host_file_parts
        user_host_parts = user_host.split('@', 1)
        if len(user_host_parts) == 1:
          user = None
          instance = user_host_parts[0]
        else:
          user, instance = user_host_parts

        # We cannot assume that the user input follows a standard
        # form, so we must canonicalize all instance references
        # ourselves. We must also ensure that instance_contexts does
        # not end up with duplicates, otherwise we could end up
        # sending duplicate Get requests for the same instance.
        instance_context = self.context['path-handler'].Parse(
            'instances', instance, zone=args.zone)
        instance_uri = self.context['path-handler'].NormalizeWithContext(
            'instances', instance_context)
        if instance_uri not in instances_added:
          instance_contexts.append(instance_context)
          instances_added.add(instance_uri)

        file_specs.append((user, instance_uri, file_path))

    logging.debug('Normalized arguments: %s', file_specs)

    # It's possible that only local files are being copied. If that's
    # the case, then we shouldn't make any API calls.
    if instance_contexts:
      self.EnsureSSHKeyIsInProject()
      instance_resources = self.GetInstances(instance_contexts)
    else:
      instance_resources = []

    # Creates a mapping of instance self links to external IP
    # addresses.
    addresses = {}
    for instance in instance_resources:
      addresses[instance.selfLink] = ssh_utils.GetExternalIPAddress(instance)

    scp_args = [
        self.scp_executable,
        '-3',  # Forces copies between remote hosts to be transferred
               # through the local host. This is necessary because the
               # remote hosts will rarely know each other's host key
               # fingerprints, so copying between remote hosts
               # directly will almost always fail with "Host key
               # verification failed".
        '-i', self.ssh_key_file,
    ]
    if args.recursive:
      scp_args.append('-r')

    # Creates the arguments for scp. In particular, at this stage, we
    # replace all instance names recorded in file_specs with their
    # external IP addresses.
    for user, instance_uri, file_path in file_specs:
      if instance_uri:
        ip_address = addresses[instance_uri]

        if user:
          scp_args.append('{0}@{1}:{2}'.format(user, ip_address, file_path))
        else:
          scp_args.append('{0}:{1}'.format(ip_address, file_path))
      else:
        scp_args.append(file_path)

    logging.debug('scp command: %s', ' '.join(scp_args))
    subprocess.check_call(scp_args)


CopyFiles.detailed_help = {
    'brief': 'Copy files to and from Google Compute Engine virtual machines',
    'DESCRIPTION': """\
        *{command}* copies files between virtual machines and your
        local machine. Under the covers, *scp(1)* is used to
        facilitate the transfer. Hosts involved can only be Compute
        Engine Virtual machines and your local machine.

        To denote a remote file, prefix the file name with the virtual
        machine instance's name (e.g., ``my-instance:~/my-file''). To
        denote a local file, do not add a prefix to the file name
        (e.g., ``~/my-file''). For example, to copy a number of remote
        files to a local directory, you can run:

          $ {command} \\
              my-instance-1:~/file-1 \\
              my-instance-2:~/file-2 \\
              ~/my-destination \\
              --zone us-central2-a

        In the above example, ``~/file-1'' from ``my-instance-1'' and
        ``~/file-2'' from ``my-instance-2'' are copied to the local
        directory ``~/my-destination''.

        Conversely, files from your local compute can be copied to the
        virtual machines:

          $ {command} \\
              ~/my-file \\
              my-instance:~/remote-destination \\
              --zone us-central2-a

        Note that the zone of the instances were provided using
        ``--zone''. It's possible to specify the zone on a
        per-instance basis by using partially-qualified
        paths:

          $ {command} \\
              us-central2-a/instances/my-instance-1:~/file-1 \\
              europe-west1-a/instnaces/my-instance-2:~/file-2 \\
              ~/my-destination

        When omitting ``--zone'', fight the urge to use full URIs for
        the instances (e.g.,
        ``https://www.googleapis.com/compute/v1/projects/my-project/zones/us-central1-a/instances/my-instance'')
        because positional arguments are split on the first colon.

        If a local file contains a colon (``:''), you can specify it
        by either using an absolute path or a path that begins with
        ``./''.

        Copies involving a remote source and a remote destination will
        go through the local host. This is done because in most cases,
        a remote source will not know the remote destination's host
        key fingerprint, so a direct copy will likely fail. If
        performance is important (e.g., large files), SSH into the
        remote destination and issue the copy command from there.
        """,
}
