# Copyright 2014 Google Inc. All Rights Reserved.
"""Context management class and path normalizer for selfLinks."""

import re


_PATH_COMPONENT_REGEXP = re.compile(r'\{[a-zA-Z0-9]+\}')


class ApiContextParser(object):
  """Parses context from fully or partially qualified paths.

  A context is simply the set of parameters necessary to specify a cloud object
  in a fully-qualified path. For instance, a disk has a fully-qualified path:
    'compute/v1/projects/{project}/zones/{zone}/disks/{disk}'

  The context is then:
    {
        'project': ...,
        'zone': ...,
        'disk': ...
    }

  Since each of these are required to fully specify which disk the user wishes
  to talk about
  """

  def __init__(self, api_host, api_context=None):
    """Initializes a new ApiContextParser.

    Arguments:
      api_host: The URL of the server hosting the API.
      api_context: A dict mapping object types in the API to paths.
    """

    self._api_host = api_host
    self._context_prompt_fxns = {}
    self._api_context = api_context

  def RegisterDefaultResolver(self, context_type, callback, priority=0):
    """Shortcut for RegisterResolver(None, context_type, callback, priority)."""
    self.RegisterResolver(None, context_type, callback, priority)

  def RegisterResolver(self, object_type, context_type, callback,
                       priority=0):
    """Add function to prompt for or detect a piece of context.

    For example,

    .RegisterResolver('disks', 'zone', AutoDetectZone)

    would use the function AutoDetectZone(context, **kwargs) to detect the zone
    for disks whenever the zone was not available in the provided path.

    If the prompt function is already set for this object_type and context_type
    then it is replaced with the specified callback.

    Args:
      object_type: Object type as listed in the api_context. If this is left
        as None then it is used as a default for all object types. An
        object-specific resolver overrides such a default resolver.
      context_type: The name of the piece of context.
      callback: Callback function accepting context and kwargs as arguments.
      priority: Optional priority for detecting this piece of context. Smaller
        priority contexts will be parsed first. If multiple pieces of context
        have the same priority, the parser will detect the most general context
        first.

    Raises:
      ValueError: Unsupported object or context type.
    """
    if object_type:
      if object_type not in self._api_context:
        raise ValueError('unsupported object type: {0}'.format(object_type))

      if context_type not in self._GetRequiredContext(object_type):
        raise ValueError(
            'unsupported context type: {0}.{1}'.format(object_type,
                                                       context_type))

    self._context_prompt_fxns[(object_type, context_type)] = (
        callback, priority)

  def _GetRequiredContext(self, object_type):
    """Parse the required context for this object type.

    Args:
      object_type: The type of object. Must be a valid compute object type.

    Returns:
      A dict with all necessary context for this kind of object.
    """
    context = {}
    for item in _PATH_COMPONENT_REGEXP.findall(self._api_context[object_type]):
      context[item[1:-1]] = None

    return context

  def _IsContext(self, path_part):
    return _PATH_COMPONENT_REGEXP.match(path_part)

  def _GetContextFromPath(self, object_type, path):
    """Get all of the context out of the path proper.

    Args:
      object_type: The type of object. Must be a valid compute object type.
      path: The path to parse.
    Returns:
      A dict with the parsed context. If a context could not be parsed,
      then None acts as a placeholder.

    Raises:
      ValueError: The path was invalid for this object type.
    """
    # Get all required context.
    context = self._GetRequiredContext(object_type)

    user_path_components = path.split('/')
    full_path_components = (
        '{0}/{1}'.format(
            self._api_host.rstrip('/'), self._api_context[object_type])
    ).split('/')

    if len(user_path_components) > len(full_path_components):
      raise ValueError('invalid path: {0}'.format(path))

    # Get all context from the path.
    for user, full in zip(reversed(user_path_components),
                          reversed(full_path_components)):
      if full and not user:
        raise ValueError('invalid path: {0}'.format(path))

      if self._IsContext(full):
        # This should be mapped to a context.
        context[full[1:-1]] = user
      else:
        # User path should match this exactly.
        if user != full:
          raise ValueError('invalid path: {0}'.format(path))

    return context

  def IdentifyObjectTypeFromPath(self, path):
    """If possible, identify the object type from the path.

    Args:
      path: Fully- or partially-qualified path to the object.

    Returns:
      The corresponding object_type if it is uniquely identifiable
      from the path. Otherwise, None.
    """
    possible_types = []

    for object_type in self._api_context:
      try:
        self._GetContextFromPath(object_type, path)
        possible_types.append(object_type)
      except ValueError:
        pass

    if len(possible_types) == 1:
      return possible_types[0]
    return None

  def _PromptForContextOrFail(self, context, object_type, path, **kwargs):
    """Get the default or user prompted context for missing parts, or fail.

    Args:
      context: The known context.
      object_type: The type of object to prompt for context for.
      path: The path that generated them.
      **kwargs: Keyword args to be passed along to the prompt functions.

    Returns:
      The parsed context.

    Raises:
      ValueError: No means of getting the context for this kind of object was
        available, and it was not specified in the path.
    """
    missing_items = []

    for item in self._GetRequiredContext(object_type):
      if context[item] is None:
        if (object_type, item) in self._context_prompt_fxns:
          # We will use the object-specific function to get the missing context.
          missing_items.append(
              (item, object_type,
               self._context_prompt_fxns[(object_type, item)][1]))
        elif (None, item) in self._context_prompt_fxns:
          # We will use the global default to get the missing context.
          missing_items.append(
              (item, None, self._context_prompt_fxns[(None, item)][1]))
        else:
          # No suitable callback to get the missing context was specified.
          raise ValueError(
              'cannot get missing context {0} from path {1}'.format(context,
                                                                    path))

    # Stably sort the missing items by priority.
    missing_items.sort(key=lambda item: item[2])

    # For each missing item, call the callback with the appropriate arguments.
    for item, lookup_type, _ in missing_items:
      context[item] = (
          self._context_prompt_fxns[(lookup_type, item)][0](context, self,
                                                            **kwargs))

    return context

  def Parse(self, object_type, path, **kwargs):
    """Either get the context for the object from the path, or fail.

    Parse will parse a (relative or fully-qualified) path
    to a compute object and return a dict with the context and object name,
    either as specified by the user in a prompt, from the flags, or in the
    path.

    For instance, suppose the user wants the context for a disk object.
    If the user specifies a path:
      'my-project/zones/some-zone/disks/my-disk',
    then the context returned will be a dict with:
      {
          project: 'my-project',
          zone: 'some-zone',
          disk: 'my-disk'
      }

    On the other hand, if the zone was not specified and the user used a less
    specific path:
      'disks/my-disk'
    depending on the callback specified in context_prompt_fxns, the user may
    be requested to specifiy the zone or it may be automatically detected,
    or perhaps it will be taken from flags.

    Args:
      object_type: The type of object. Must be a valid compute object type.
      path: A relative or absolute path to the object.
      **kwargs: Keyword args to be passed along to the callbacks if necessary.

    Returns:
      A dict with all necessary context path parsed out, or alternatively the
      context from flags.

    Raises:
      ValueError: Nonexistent context type.
    """
    # Ensure that this is a real object type.
    if object_type not in self._api_context:
      raise ValueError('unsupported object type: {0}'.format(object_type))

    # Get all context from the path.
    context = self._GetContextFromPath(object_type, path)

    # For each context that could not be taken from the path, prompt for it
    # or get it from flags.
    context = self._PromptForContextOrFail(context, object_type, path, **kwargs)

    return context

  def Normalize(self, object_type, path, **kwargs):
    """Either get the normalized for the object from the path, or fail.

    Normalize will parse a (relative or fully-qualified) path
    to a compute object and return a dict with the context and object name,
    either as specified by the user in a prompt, from the flags, or in the
    path.

    Args:
      object_type: The type of object. Must be a valid compute object type.
      path: A relative or absolute path to the object.
      **kwargs: Keyword args to be passed along to callbacks if necessary.

    Returns:
      A string which equals the normalized path.
    """
    if path is None:
      return

    context = self.Parse(object_type, path, **kwargs)

    return self.NormalizeWithContext(object_type, context)

  def NormalizeWithContext(self, object_type, context):
    """Given some context, produce a normalized path.

    Args:
      object_type: The type of object. Must be a valid compute object type.
      context: A dictionary of context to use.

    Returns:
      A string which equals the normalized path.
    """

    relative_path = self._api_context[object_type].format(**context)

    return '{0}/{1}'.format(self._api_host.rstrip('/'), relative_path)
