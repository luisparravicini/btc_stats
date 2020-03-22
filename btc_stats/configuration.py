import yaml
from pathlib import Path


def read_conf(env_name):
    conf_path = Path('conf', env_name + '.yaml')
    with open(conf_path) as file:
        conf = yaml.safe_load(file)

    return conf


def path_from_conf(conf_path):
    cdir = Path(__file__).parent.joinpath(conf_path)
    cdir.mkdir(exist_ok=True)
    return cdir
