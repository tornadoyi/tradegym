from setuptools import setup, find_packages

# Project name
NAME = 'tradegym'


setup(
    name=NAME,
    version='0.1',
    description="gym environment for finance trading",
    author='Yi Gu',
    license='License :: OSI Approved :: Apache Software License',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.10',
    install_requires=[
        'gymnasium',
        'pandas',
    ],
    entry_points={
		'console_scripts': [
            'tradegym = tradegym.cli:main',
		],
	},
    package_data = {
        'tradegym/config': ["tradegym/config/*"]
    }

)