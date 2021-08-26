from setuptools import setup

setup(
    name='Ignite Nlu Server',
    version='1.0.0-alpha.0',
    packages=['server'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools_rust',
        'Flask',
        'PyExecJs',
        'snips-nlu',
    ],
    python_requires='>=3, <3.9',
)
