# Copyright 2014 Google Inc. All Rights Reserved.

"""Utilities for subcommands that need to SSH into virtual machine guests."""
import abc
import getpass
import os
import subprocess

from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import metadata_utils
from googlecloudsdk.compute.lib import path_simplifier
from googlecloudsdk.compute.lib import request_helper
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import console_io
from googlecloudsdk.core.util import files


def GetExternalIPAddress(instance_resource):
  """Returns the external IP address of the instance or raises."""
  if instance_resource.networkInterfaces:
    access_configs = instance_resource.networkInterfaces[0].accessConfigs
    if access_configs:
      return access_configs[0].natIP

  raise exceptions.ToolException(
      'instance {0} in zone {1} does not have an external IP address, so you '
      'cannot SSH into it; To add an external IP address to the instance, use '
      '"gcloud compute instances add-access-config"'
      .format(instance_resource.name,
              path_simplifier.Name(instance_resource.zone)))


def _GetSSHKeysFromMetadata(metadata):
  """Returns the value of the "sshKeys" metadata as a list."""
  if not metadata:
    return []
  for item in metadata.items:
    if item.key == constants.SSH_KEYS_METADATA_KEY:
      return [key.strip() for key in item.value.split('\n') if key]
  return []


def _PrepareSSHKeysValue(ssh_keys):
  """Returns a string appropriate for the metadata.

  Values from are taken from the tail until either all values are
  taken or _MAX_METADATA_VALUE_SIZE_IN_BYTES is reached, whichever
  comes first. The selected values are then reversed. Only values at
  the head of the list will be subject to removal.

  Args:
    ssh_keys: A list of keys. Each entry should be one key.

  Returns:
    A new-line-joined string of SSH keys.
  """
  keys = []
  bytes_consumed = 0

  for key in reversed(ssh_keys):
    num_bytes = len(key + '\n')
    if bytes_consumed + num_bytes > constants.MAX_METADATA_VALUE_SIZE_IN_BYTES:
      log.warn('The following SSH key will be removed from your project '
               'because your sshKeys metadata value has reached its '
               'maximum allowed size of {0} bytes: {1}'
               .format(constants.MAX_METADATA_VALUE_SIZE_IN_BYTES, key))
    else:
      keys.append(key)
      bytes_consumed += num_bytes

  keys.reverse()
  return '\n'.join(keys)


def _AddSSHKeyToMetadataMessage(metadata, public_key):
  """Adds the public key material to the metadata if it's not already there."""
  entry = '{user}:{public_key}'.format(
      user=getpass.getuser(), public_key=public_key)

  ssh_keys = _GetSSHKeysFromMetadata(metadata)
  log.debug('Current SSH keys in project: {0}'.format(ssh_keys))

  if entry in ssh_keys:
    return metadata
  else:
    ssh_keys.append(entry)
    return metadata_utils.ConstructMetadataMessage(
        metadata={
            constants.SSH_KEYS_METADATA_KEY: _PrepareSSHKeysValue(ssh_keys)},
        existing_metadata=metadata)


class BaseSSHCommand(base.Command):
  """Base class for subcommands that need to SSH into a guest.

  Subclasses can call EnsureSSHKeyIsInProject() to make sure that the
  user's public SSH key is placed in the project metadata before
  proceeding. EnsureSSHKeyIsInProject() depends on an abstract method
  GetPublicKey(). GetPublicKey() should return the user's public SSH
  key and offer to generate one if a key does not exist.
  """

  __meta__ = abc.ABCMeta

  def GetProject(self):
    """Returns the project object."""
    objects = list(request_helper.MakeRequests(
        requests=[(self.context['compute'].projects,
                   'Get',
                   messages.ComputeProjectsGetRequest(
                       project=properties.VALUES.core.project.Get(
                           required=True),
                   ))],
        http=self.context['http'],
        batch_url=self.context['batch-url']))
    return objects[0]

  def SetProjectMetadata(self, new_metadata):
    """Sets the project metadata to the new metadata."""
    compute = self.context['compute']

    list(request_helper.MakeRequests(
        requests=[(compute.projects,
                   'SetCommonInstanceMetadata',
                   messages.ComputeProjectsSetCommonInstanceMetadataRequest(
                       metadata=new_metadata,
                       project=properties.VALUES.core.project.Get(
                           required=True),
                   ))],
        http=self.context['http'],
        batch_url=self.context['batch-url']))

  def GetInstances(self, instance_contexts):
    """Returns the instance resources for the given instance contexts."""
    requests = []
    for instance_context in instance_contexts:
      requests.append((self.context['compute'].instances,
                       'Get',
                       messages.ComputeInstancesGetRequest(
                           instance=instance_context['instance'],
                           project=instance_context['project'],
                           zone=instance_context['zone'])))

    objects = list(request_helper.MakeRequests(
        requests=requests,
        http=self.context['http'],
        batch_url=self.context['batch-url']))
    return objects

  @abc.abstractmethod
  def GetPublicKey(self):
    """Creates (if needed) and returns the public SSH key as a string."""

  def EnsureSSHKeyIsInProject(self):
    # First, grab the public key from the user's computer. If the
    # public key doesn't already exist, GetPublicKey() should create
    # it.
    public_key = self.GetPublicKey()

    # Second, let's make sure the public key is in the project metadata.
    project = self.GetProject()
    existing_metadata = project.commonInstanceMetadata
    new_metadata = _AddSSHKeyToMetadataMessage(existing_metadata, public_key)
    if new_metadata != existing_metadata:
      self.SetProjectMetadata(new_metadata)

  @abc.abstractmethod
  def Run(self, args):
    pass


class BaseSSHCommandForClientsWithOpenSSHSupport(BaseSSHCommand):
  """Base class for SSH commands targeted for systems that have OpenSSH support.

  The target systems include Linux and Mac OS X.
  """

  __meta__ = abc.ABCMeta

  @staticmethod
  def Args(parser):
    ssh_key_file = parser.add_argument(
        '--ssh-key-file',
        help='The path to the SSH key file.')
    ssh_key_file.detailed_help = """\
        The path to the SSH key file. By deault, this is ``{0}''.
        """.format(constants.DEFAULT_SSH_KEY_FILE)

  def GetPublicKey(self):
    """Generates an SSH key using ssh-key (if necessary) and returns it."""
    public_ssh_key_file = self.ssh_key_file + '.pub'
    if (not os.path.exists(self.ssh_key_file) or
        not os.path.exists(public_ssh_key_file)):
      log.warn('You do not have an SSH key for Google Compute Engine.')
      log.warn('ssh-keygen will be executed to generate a key.')

      ssh_directory = os.path.dirname(public_ssh_key_file)
      if not os.path.exists(ssh_directory):
        if console_io.PromptContinue(
            'This tool needs to create the directory {0} before being able to '
            'generate SSH keys.'.format(ssh_directory)):
          files.MakeDir(ssh_directory)
        else:
          raise exceptions.ToolException('SSH key generation aborted by user')

      try:
        subprocess.check_call([
            self.ssh_keygen_executable,
            '-t', 'rsa',
            '-f', self.ssh_key_file,
        ])
      except OSError as e:
        raise exceptions.ToolException(
            'there was a problem running ssh-keygen: {0}'.format(e.strerror))
      except subprocess.CalledProcessError as e:
        raise exceptions.ToolException(
            'ssh-keygen exited with return code {0}'.format(e.returncode))

    with open(public_ssh_key_file) as f:
      return f.read().strip()

  def Run(self, args):
    """Subclasses must call this in their Run() before continuing."""
    self.scp_executable = files.FindExecutableOnPath('scp')
    self.ssh_executable = files.FindExecutableOnPath('ssh')
    self.ssh_keygen_executable = files.FindExecutableOnPath('ssh-keygen')
    if (not self.scp_executable or
        not self.ssh_executable or
        not self.ssh_keygen_executable):
      raise exceptions.ToolException('your platform does not support OpenSSH')

    self.ssh_key_file = os.path.realpath(os.path.expanduser(
        args.ssh_key_file or constants.DEFAULT_SSH_KEY_FILE))

