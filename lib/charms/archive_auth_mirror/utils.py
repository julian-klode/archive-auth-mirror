import os
from pathlib import Path
import shutil

from charmhelpers.core import hookenv
from charmhelpers.core import host


def get_paths(base_dir=None):
    """Return path for the service tree.

    The filesystem tree for the service is as follows:

    /srv/archive-auth-mirror
    ├── basic-auth -- the file containing BasicAuth username/passwords
    ├── bin
    │   └── mirror-archive  -- the mirroring script
    ├── config  -- the script configuration file
    ├── reprepro
    │   └── conf  -- reprepro configuration files
    │       └── .gnupg  -- GPG config for reprepro
    └── static  -- the root of the virtualhost, contains the repository
    """
    if base_dir is None:
        base_dir = '/srv/archive-auth-mirror'
    base_dir = Path(base_dir)
    reprepro_dir = base_dir / 'reprepro'
    return {
        'base': base_dir,
        'bin': base_dir / 'bin',
        'config': base_dir / 'config',
        'reprepro': reprepro_dir,
        'reprepro-conf': reprepro_dir / 'conf',
        'static': base_dir / 'static',
        'gnupghome': reprepro_dir / '.gnupg',
        'basic-auth': base_dir / 'basic-auth'}


def get_virtualhost_name(hookenv=hookenv):
    """Return the configured service URL or the unit address."""
    service_url = hookenv.config().get('service-url')
    return service_url or hookenv.unit_public_ip()


def get_virtualhost_config(hookenv=hookenv):
    """Return the configuration for the static virtuahost."""
    paths = get_paths()
    domain = get_virtualhost_name(hookenv=hookenv)
    return {
        'domain': domain,
        'document_root': str(paths['static']),
        'basic_auth_file': str(paths['basic-auth'])}


def install_resources(base_dir=None):
    """Create tree structure and copy resources from the charm."""
    paths = get_paths(base_dir=base_dir)
    for name in ('bin', 'reprepro-conf', 'static'):
        host.mkdir(str(paths[name]), perms=0o755)

    # the gpg directory should only be readable by root
    host.mkdir(str(paths['gnupghome']), perms=0o700)

    # create an empty basic-auth password file. It will be updated by a script
    # run as root, but it must be readable by the web server
    host.write_file(
        str(paths['basic-auth']), b'', group='www-data', perms=0o640)

    # copy scripts
    for resource in ('mirror-archive', 'manage-user'):
        resource_path = os.path.join('resources', resource)
        shutil.copy(resource_path, str(paths['bin']))