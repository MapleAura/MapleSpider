from setuptools import setup, find_packages

setup(
    name='maple_crawler',
    version='0.1.0',
    description='Modular crawler framework with XHS plugin',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    install_requires=[
        'playwright',
        'requests',
        'beautifulsoup4',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'crawler=maple_crawler.cli:main'
        ]
    },
    author='Generated',
)
