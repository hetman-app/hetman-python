from setuptools import find_packages, setup

setup(
    name='hetman',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    author='yaria.pl',
    author_email='dev@hetman.app',
    description='Official Python integration with Hetman.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hetman-app/hetman-python',
    license='Apache',
    python_requires='>=3.6'
)
