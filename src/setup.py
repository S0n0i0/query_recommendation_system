from distutils.core import setup

with open("README.txt") as f:
    readme = f.read()

    setup(name='src',
        version='1.0',
        description='Data mining project',
        long_description=readme,
        author='Ribaga and Compri',
        url='https://github.com/S0n0i0/DM22_240180_239953',
        packages=['src'],
        install_requires=["pandas"], #external packages as dependencies
        )