#! boto_version_check.py
"""
This module simply attempts to import botocore and boto3 and to report their respective versions.

This is required because in serverless deployments we rely on the AWDS lambda environment to have teh pre-installed
in the lambda PythonX installation. But this has recently lead to some version conflicts :

e.g.
 - https://stackoverflow.com/questions/75887656/
   botocore-package-in-lambda-python-3-9-runtime-return-error-cannot-import-name
 - https://github.com/boto/boto3/issues/3648

Hopefully logging output from this modulw will aid in diagnosing such issues in the future.
"""

import importlib.util
import logging
import sys

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)


# from https://docs.python.org/3/library/importlib.html#importing-programmatically
def lazy_import(name):
    spec = importlib.util.find_spec(name)
    log.info('module %s has spec" %s ' % (name, spec))
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


for name in ['botocore', 'boto3']:
    lib = lazy_import('botocore')
    log.info('library: "%s" has version: %s' % (name, lib.__version__))
