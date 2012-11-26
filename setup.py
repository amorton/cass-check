from setuptools import setup

entry_points = """
[console_scripts]
cass-check = cass_check.scripts:cass_check_main

[cass_check.commands]
noop=cass_check.commands:NoopCommand
check=cass_check.commands:CheckCommand
collect=cass_check.commands:CollectCommand

[cass_check.tasks.collection]
logs=cass_check.collection_tasks:LogCollectionTask
proxy_histograms=cass_check.collection_tasks:ProxyHistogramsCollectionTask
"""

setup(
    name='cass-check',
    version='0.0.1',
    author='Aaron Morton',
    author_email='aaron@thelastpickle.com',
    packages = [],
    install_requires=[
        "PyYAML>=3.10"
    ],
    entry_points=entry_points
)
