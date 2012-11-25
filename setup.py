from setuptools import setup

entry_points = """
[console_scripts]
cass-check = cass_check.scripts:cass_check_main

[cass_check.commands]
noop=cass_check.commands:NoopCommand
"""

setup(
    name='cass-check',
    version='0.0.1',
    author='Aaron Morton',
    author_email='aaron@thelastpickle.com',
    packages = [],
    entry_points=entry_points
)
