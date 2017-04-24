"""
Deploy a new function to lambda
Basically copy-paste from python-lambda repo
TODO: Fork this properly
Needs YAML config with:
- aws_access_key_id
- aws_secret_access_key
- runtime: python3.6
- region: eu-central-1
- modules - array of local modules to copy to package
- main_path - path where modules to be copied are stored
- requirements - path to requirements file
- function_name - lambda unique name

DISCLAIMER: Don't install from repo - it breaks boto

FIXME: Very shamefull copy-paste
"""

from __future__ import print_function
import json
import logging
import os
import zipfile
import datetime as dt
import time
from imp import load_source
from shutil import copy, copyfile
from tempfile import mkdtemp

import botocore
import boto3
import pip
import yaml


log = logging.getLogger(__name__)


def cleanup_old_versions(src, keep_last_versions):
    """Deletes old deployed versions of the function in AWS Lambda.

    Won't delete $Latest and any aliased version

    :param str src:
        The path to your Lambda ready project (folder must contain a valid
        config.yaml and handler module (e.g.: service.py).
    :param int keep_last_versions:
        The number of recent versions to keep and not delete
    """
    if keep_last_versions <= 0:
        print("Won't delete all versions. Please do this manually")
    else:
        path_to_config_file = os.path.join(src, 'config.yaml')
        cfg = read(path_to_config_file, loader=yaml.load)

        aws_access_key_id = cfg.get('aws_access_key_id')
        aws_secret_access_key = cfg.get('aws_secret_access_key')

        client = get_client('lambda', aws_access_key_id, aws_secret_access_key,
                            cfg.get('region'))

        response = client.list_versions_by_function(
            FunctionName=cfg.get("function_name")
        )
        versions = response.get("Versions")
        if len(response.get("Versions")) < keep_last_versions:
            print("Nothing to delete. (Too few versions published)")
        else:
            version_numbers = [elem.get("Version") for elem in
                               versions[1:-keep_last_versions]]
            for version_number in version_numbers:
                try:
                    client.delete_function(
                        FunctionName=cfg.get("function_name"),
                        Qualifier=version_number
                    )
                except botocore.exceptions.ClientError as e:
                    print("Skipping Version {}: {}".format(version_number,
                                                              e.message))


def deploy(local_package=None):
    """Deploys a new function to AWS Lambda.

    :param str src:
        The path to your Lambda ready project (folder must contain a valid
        config.yaml and handler module (e.g.: service.py).
    :param str local_package:
        The path to a local package with should be included in the deploy as
        well (and/or is not available on PyPi)
    """
    # Load and parse the config file.
    path_to_config_file = os.path.join(src, 'config.yaml')
    cfg = read(path_to_config_file, loader=yaml.load)

    # Copy all the pip dependencies required to run your code into a temporary
    # folder then add the handler file in the root of this directory.
    # Zip the contents of this folder into a single file and output to the dist
    # directory.
    path_to_zip_file = build(src, local_package)

    print(path_to_zip_file)
    if function_exists(cfg, cfg.get('function_name')):
        update_function(cfg, path_to_zip_file)
    else:
        create_function(cfg, path_to_zip_file)


def invoke(src, alt_event=None, verbose=False):
    """Simulates a call to your function.

    :param str src:
        The path to your Lambda ready project (folder must contain a valid
        config.yaml and handler module (e.g.: service.py).
    :param str alt_event:
        An optional argument to override which event file to use.
    :param bool verbose:
        Whether to print out verbose details.
    """
    # Load and parse the config file.
    path_to_config_file = os.path.join(src, 'config.yaml')
    cfg = read(path_to_config_file, loader=yaml.load)

    # Load and parse event file.
    if alt_event:
        path_to_event_file = os.path.join(src, alt_event)
    else:
        path_to_event_file = os.path.join(src, 'event.json')
    event = read(path_to_event_file, loader=json.loads)

    handler = cfg.get('handler')
    # Inspect the handler string (<module>.<function name>) and translate it
    # into a function we can execute.
    fn = get_callable_handler_function(src, handler)

    # TODO: look into mocking the ``context`` variable, currently being passed
    # as None.

    start = time.time()
    results = fn(event, None)
    end = time.time()

    print("{0}".format(results))
    if verbose:
        print("\nexecution time: {:.8f}s\nfunction execution "
              "timeout: {:2}s".format(end - start, cfg.get('timeout', 15)))


def init(src, minimal=False):
    """Copies template files to a given directory.

    :param str src:
        The path to output the template lambda project files.
    :param bool minimal:
        Minimal possible template files (excludes event.json).
    """

    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "project_templates")
    for filename in os.listdir(templates_path):
        if (minimal and filename == 'event.json') or filename.endswith('.pyc'):
            continue
        destination = os.path.join(templates_path, filename)
        copy(destination, src)


def build(src, local_package=None):
    """Builds the file bundle.

    :param str src:
       The path to your Lambda ready project (folder must contain a valid
        config.yaml and handler module (e.g.: service.py).
    :param str local_package:
        The path to a local package with should be included in the deploy as
        well (and/or is not available on PyPi)
    """
    # Load and parse the config file.
    path_to_config_file = os.path.join(src, 'config.yaml')
    cfg = read(path_to_config_file, loader=yaml.load)

    # Get the absolute path to the output directory and create it if it doesn't
    # already exist.
    dist_directory = cfg.get('dist_directory', 'dist')
    path_to_dist = os.path.join(src, dist_directory)
    mkdir(path_to_dist)

    # Combine the name of the Lambda function with the current timestamp to use
    # for the output filename.
    function_name = cfg.get('function_name')
    output_filename = "{0}-{1}.zip".format(timestamp(), function_name)

    path_to_temp = mkdtemp(prefix='aws-lambda')
    os.mkdir(os.path.join(path_to_temp, 'lib'))
    os.mkdir(os.path.join(path_to_temp, 'lib', 'python')) 
    print(path_to_temp)
    print(os.path.join(path_to_temp, 'lib'))
    print(os.path.join(path_to_temp, 'lib', 'python'))
    pip_install_to_target(path_to_temp, cfg, local_package)

    # Gracefully handle whether ".zip" was included in the filename or not.
    output_filename = ('{0}.zip'.format(output_filename)
                       if not output_filename.endswith('.zip')
                       else output_filename)

    files = []
    for filename in os.listdir(src):
        if os.path.isfile(filename):
            if filename == '.DS_Store':
                continue
            if filename == 'config.yaml':
                continue
            files.append(os.path.join(src, filename))

    import shutil
    for module in cfg.get('modules'):
        shutil.copytree(
            os.path.join(cfg.get('main_path'), module),
            os.path.join(path_to_temp, module)
        )

    # "cd" into `temp_path` directory.
    os.chdir(path_to_temp)
    for f in files:
        _, filename = os.path.split(f)

        # Copy handler file into root of the packages folder.
        copyfile(f, os.path.join(path_to_temp, filename))

    # Zip them together into a single file.
    # TODO: Delete temp directory created once the archive has been compiled.
    path_to_zip_file = archive('./', path_to_dist, output_filename)
    return path_to_zip_file


def get_callable_handler_function(src, handler):
    """Tranlate a string of the form "module.function" into a callable
    function.

    :param str src:
      The path to your Lambda project containing a valid handler file.
    :param str handler:
      A dot delimited string representing the `<module>.<function name>`.
    """

    # "cd" into `src` directory.
    os.chdir(src)

    module_name, function_name = handler.split('.')
    filename = get_handler_filename(handler)

    path_to_module_file = os.path.join(src, filename)
    module = load_source(module_name, path_to_module_file)
    return getattr(module, function_name)


def get_handler_filename(handler):
    """Shortcut to get the filename from the handler string.

    :param str handler:
      A dot delimited string representing the `<module>.<function name>`.
    """
    module_name, _ = handler.split('.')
    return '{0}.py'.format(module_name)


def pip_install_to_target(path, cfg, local_package=None):
    """For a given active virtualenv, gather all installed pip packages then
    copy (re-install) them to the path provided.

    :param str path:
        Path to copy installed pip packages to.
    :param str local_package:
        The path to a local package with should be included in the deploy as
        well (and/or is not available on PyPi)
    """
    print('Gathering pip packages')

    f = open(cfg.get('requirements'), 'r')
    for r in f:
        if r.startswith('Python=='):
            # For some reason Python is coming up in pip freeze.
            continue
        elif r.startswith('-e '):
            r = r.replace('-e ','')

        print('Installing {package}'.format(package=r))
        print(path)
        pip.main(['install', r, '-t', path, '--ignore-installed'])

    f.close()
    if local_package is not None:
        pip.main(['install', local_package, '-t', path])


def get_role_name(account_id, role):
    """Shortcut to insert the `account_id` and `role` into the iam string."""
    return "arn:aws:iam::{0}:role/{1}".format(account_id, role)


def get_account_id(aws_access_key_id, aws_secret_access_key):
    """Query STS for a users' account_id"""
    client = get_client('sts', aws_access_key_id, aws_secret_access_key)
    return client.get_caller_identity().get('Account')


def get_client(client, aws_access_key_id, aws_secret_access_key, region=None):
    """Shortcut for getting an initialized instance of the boto3 client."""

    return boto3.client(
        client,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region
    )


def create_function(cfg, path_to_zip_file):
    """Register and upload a function to AWS Lambda."""

    print("Creating your new Lambda function")
    byte_stream = read(path_to_zip_file)

    aws_access_key_id = cfg.get('aws_access_key_id')
    aws_secret_access_key = cfg.get('aws_secret_access_key')

    client = get_client('lambda', aws_access_key_id, aws_secret_access_key,
                        cfg.get('region'))

    client.create_function(
        FunctionName=cfg.get('function_name'),
        Runtime=cfg.get('runtime', 'python2.7'),
        Role='arn:aws:iam::202913470273:role/lambda_image_test',
        Handler=cfg.get('handler'),
        Code={'ZipFile': byte_stream},
        Description=cfg.get('description'),
        Timeout=cfg.get('timeout', 15),
        MemorySize=cfg.get('memory_size', 512),
        Publish=True
    )


def update_function(cfg, path_to_zip_file):
    """Updates the code of an existing Lambda function"""

    print("Updating your Lambda function")
    byte_stream = read(path_to_zip_file)
    aws_access_key_id = cfg.get('aws_access_key_id')
    aws_secret_access_key = cfg.get('aws_secret_access_key')

    account_id = get_account_id(aws_access_key_id, aws_secret_access_key)
    role = get_role_name(account_id, cfg.get('role', 'lambda_basic_execution'))

    client = get_client('lambda', aws_access_key_id, aws_secret_access_key,
                        cfg.get('region'))

    client.update_function_code(
        FunctionName=cfg.get('function_name'),
        ZipFile=byte_stream,
        Publish=True
    )

    client.update_function_configuration(
        FunctionName=cfg.get('function_name'),
        Role='arn:aws:iam::202913470273:role/lambda_image_test',
        Handler=cfg.get('handler'),
        Description=cfg.get('description'),
        Timeout=cfg.get('timeout', 15),
        MemorySize=cfg.get('memory_size', 512)
    )


def function_exists(cfg, function_name):
    """Check whether a function exists or not"""

    aws_access_key_id = cfg.get('aws_access_key_id')
    aws_secret_access_key = cfg.get('aws_secret_access_key')
    client = get_client('lambda', aws_access_key_id, aws_secret_access_key,
                        cfg.get('region'))
    functions = client.list_functions().get('Functions', [])
    for fn in functions:
        if fn.get('FunctionName') == function_name:
            return True
    return False

# Helpers

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def read(path, loader=None):
    with open(path, 'rb') as fh:
        if not loader:
            return fh.read()
        return loader(fh.read())


def archive(src, dest, filename):
    output = os.path.join(dest, filename)
    zfh = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)

    for root, _, files in os.walk(src):
        for file in files:
            zfh.write(os.path.join(root, file))
    zfh.close()
    return os.path.join(dest, filename)


def timestamp(fmt='%Y-%m-%d-%H%M%S'):
    now = dt.datetime.utcnow()
    return now.strftime(fmt)

if __name__ == '__main__':
    src = os.path.dirname(os.path.realpath(__file__))
    path_to_config_file = os.path.join(src, 'config.yaml')
    cfg = read(path_to_config_file, loader=yaml.load)
    update_function(cfg, 
        '/home/ec2-user/aws-images-test/aws-test-zip.zip')
    #deploy(src)