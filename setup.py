from setuptools import setup

setup(
    name='pagenize',
    version='0.0.1',
    install_requires=['click', 'tqdm'],
    entry_points={
        'console_scripts': [
            'pagenize = pagenize:pagenize'
        ]
    }
)
