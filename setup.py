from setuptools import setup
from glob import glob
import os
from hera_op import version
import json

data = [version.git_origin, version.git_hash, version.git_description, version.git_branch]
with open(os.path.join('hera_op', 'GIT_INFO'), 'w') as outfile:
    json.dump(data, outfile)

def package_files(package_dir, subdirectory):
    # walk the input package_dir/subdirectory
    # return a package_data list
    paths = []
    directory = os.path.join(package_dir, subdirectory)
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            path = path.replace(package_dir + '/', '')
            paths.append(os.path.join(path, filename))
    return paths
data_files = package_files('hera_op', 'data')

setup_args = {
    'name': 'hera_op',
    'author': 'HERA Team',
    'url': 'https://github.com/HERA-Team/hera_op',
    'license': 'BSD',
    'description': 'offline-processing and pipeline managment for HERA data analysis',
    'package_dir': {'hera_op': 'hera_op'},
    'packages': ['hera_op'],
    'include_package_data': True,
    'scripts': glob('scripts/*.py') + glob('scripts/*.sh'),
    'version': version.version,
    'package_data': {'hera_op': data_files},
    'zip_safe': False,
}

if __name__ == '__main__':
    apply(setup, (), setup_args)
