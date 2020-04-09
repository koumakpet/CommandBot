import logging
import os
from typing import Dict, List

import yaml

# Paths
BOT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BOT_DIR, os.pardir))
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.yaml')

log = logging.getLogger(__name__)


def _env_var_constructor(loader, node):
    '''
    Implements a custom YAML tag for loading optional environment
    variables. If the environment variable is set, returns the
    value of it. Otherwise, returns `None`.

    Example usage in the YAML configuration:

        # Optional app configuration. Set `MY_APP_KEY` in the environment to use it.
        application:
            key: !ENV 'MY_APP_KEY'
    '''

    default = None

    # Check if the node is a plain string value
    if node.id == 'scalar':
        value = loader.construct_scalar(node)
        key = str(value)
    else:
        # The node value is a list
        value = loader.construct_sequence(node)

        if len(value) >= 2:
            # If we have at least two values, then we have both a key and a default value
            default = value[1]
            key = value[0]
        else:
            # Otherwise, we just have a key
            key = value[0]

    return os.getenv(key, default)


yaml.SafeLoader.add_constructor('!ENV', _env_var_constructor)

with open(CONFIG_FILE, encoding='UTF-8') as f:
    _CONFIG_YAML = yaml.safe_load(f)


class YAMLGetter(type):
    '''
    Implements a custom metaclass used for accessing
    configuration data by simply accessing class attributes.
    Supports getting configuration from up to two levels
    of nested configuration through `section` and `subsection`.

    `section` specifies the YAML configuration section (or 'key')
    in which the configuration lives, and must be set.

    `subsection` is an optional attribute specifying the section
    within the section from which configuration should be loaded.

    Example Usage:

        # config.yml
        bot:
            prefixes:
                direct_message: ''
                guild: '!'

        # config.py
        class Prefixes(metaclass=YAMLGetter):
            section = 'bot'
            subsection = 'prefixes'

        # Usage in Python code
        from config import Prefixes
        def get_prefix(bot, message):
            if isinstance(message.channel, PrivateChannel):
                return Prefixes.direct_message
            return Prefixes.guild
    '''

    subsection = None

    def __getattr__(cls, name):
        name = name.lower()

        try:
            if cls.subsection is not None:
                return _CONFIG_YAML[cls.section][cls.subsection][name]
            return _CONFIG_YAML[cls.section][name]
        except KeyError:
            dotted_path = '.'.join(
                (cls.section, cls.subsection, name)
                if cls.subsection is not None else (cls.section, name)
            )
            log.critical(f'Tried accessing configuration variable at `{dotted_path}`, but it could not be found.')
            raise

    def __getitem__(cls, name):
        return cls.__getattr__(name)

    def __iter__(cls):
        '''Return generator of key: value pairs of current constants class' config values.'''
        for name in cls.__annotations__:
            yield name, getattr(cls, name)


class Bot(metaclass=YAMLGetter):
    section = 'bot'

    prefix: str
    token: str


class Guild(metaclass=YAMLGetter):
    section = 'guild'

    id: int
    moderation_channels: List[int]
    staff_channels: List[int]

    moderation_roles: List[int]
    staff_roles: List[int]


class Roles(metaclass=YAMLGetter):
    section = 'guild'
    subsection = 'roles'

    guests: int
    members: int
    owners: int
    admins: int
    mods: int
    trial_mods: int
    muted: int
    announcements: int


class Channels(metaclass=YAMLGetter):
    section = 'guild'
    subsection = 'channels'

    announcements: int

    off_topic: int
    ask_for_help: int
    commands: int

    admins: int
    mods: int

    support: int
    suggestions: int
    report: int

    attachment_log: int
    message_log: int
    user_log: int
    mod_log: int


class AntiSpam(metaclass=YAMLGetter):
    section = 'anti_spam'

    punishment: Dict[str, Dict[str, int]]
    rules: Dict[str, Dict[str, int]]
    role_whitelist: List[int]


class Filter(metaclass=YAMLGetter):
    section = 'filter'

    domain_blacklist: List[int]
    word_watchlist: List[int]

    channel_whitelist: List[int]
    role_whitelist: List[int]


class AntiMalware(metaclass=YAMLGetter):
    section = 'anti_malware'

    whitelist: list


class Emoji(metaclass=YAMLGetter):
    section = 'style'
    subsection = 'emojis'

    defcon_disabled: str
    defcon_enabled: str
    defcon_updated: str

    status_online: str
    status_idle: str
    status_dnd: str
    status_offline: str

    bullet: str
    pencil: str
    new: str
    cross_mark: str
    check_mark: str

    upvotes: str
    comments: str
    user: str


class Icons(metaclass=YAMLGetter):
    section = 'style'
    subsection = 'icons'

    message_bulk_delete: str
    message_delete: str
    message_edit: str

    sign_in: str
    sign_out: str

    filtering: str

    user_ban: str
    user_unban: str
    user_update: str
    user_mute: str
    user_unmute: str
    user_warn: str

    hash_blupre: str
    hash_green: str
    hash_red: str

    defcon_denied: str
    defcon_disabled: str
    defcon_enables: str
    defcon_updated: str


# Some vars
MODERATION_ROLES = Guild.moderation_roles
STAFF_ROLES = Guild.staff_channels

MODERATION_CHANNELS = Guild.moderation_channels
STAFF_CHANNELS = Guild.staff_channels