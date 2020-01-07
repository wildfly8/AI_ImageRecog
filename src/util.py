import json
import os
import pymysql
import sqlalchemy as sa
from sqlalchemy import exc as sa_exc
import warnings

#needed to avoid a sqlalchemy error
pymysql.install_as_MySQLdb()
warnings.simplefilter("ignore", category=sa_exc.SAWarning)


def get_config():

    # Check if file contents are cached
    if hasattr(get_config, "config"):
        return get_config.config
    else:
        get_config.config = None

    # Read in config file
    is_windows = os.name == 'nt'
    cfg_file_path = None

    # Get path for config file (attempt to use environment variable: SECRETS_LOCATION)
    if not os.getenv('SECRETS_LOCATION'):
        if is_windows:
            cfg_file_path = r'{}\{}'.format(
                os.getenv('APPDATA'), 'config.json'
            )
        else:
            cfg_file_path = "/var/run/config.json"
    else:
        if is_windows:
            cfg_file_path = r'{}\{}'.format(
                os.getenv('SECRETS_LOCATION'), 'config.json'
            )
        else:
            cfg_file_path = r'{}/{}'.format(
                os.getenv('SECRETS_LOCATION'), 'config.json'
            )

    # Read/cache config file and return as dictionary
    with open('{}'.format(cfg_file_path), 'r') as stream:
        try:
            get_config.config = json.loads(stream.read())
        except Exception as exc:
            print(exc)
            exit(1)

    return get_config.config


def create_memsql_engine(cfg=None):
    if cfg is None:
        cfg = get_config()
        cfg = cfg['memsql']
    conn_str = cfg['user'] + ":" + cfg['password'] + "@" + cfg['host'] + "/" + cfg['database']
    return sa.create_engine(
        "mysql://" + conn_str,
        strategy="threadlocal", pool_size=2,
        max_overflow=1, pool_timeout=0, pool_recycle=180
    )
