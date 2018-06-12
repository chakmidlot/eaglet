from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='eaglet',
      version='0.1',
      description='Copies data from one folder to another with encription and back.',
      author='chakmidlot',
      author_email='chakmidlot@gmail.com',
      url='',
      packages=find_packages(),
      scripts=['bin/eaglet'],
      install_requires=requirements,
)
