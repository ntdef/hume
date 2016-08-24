"""
A containerized interface for machine learning.
"""
from setuptools import find_packages, setup

dependencies = ['docopt']

setup(
    name='hume',
    version='0.1.2-alpha',
    url='https://github.com/ntdef/hume',
    download_url='https://github.com/ntdef/hume/archive/v0.1.2-alpha.tar.gz',
    license='MIT',
    author='Troy de Freitas',
    description='A containerized interface for machine learning',
    long_description=__doc__,
    packages=find_packages(exclude=['tests', 'examples']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'hume = hume.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
