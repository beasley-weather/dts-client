from setuptools import setup


setup(
    name='dts-client',
    packages=['dts_client'],
    include_package_data=True,
    install_requires=[
        'requests',
        'weewx-orm'
    ]
)
