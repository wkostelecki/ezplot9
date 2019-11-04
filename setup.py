from setuptools import setup, find_packages

with open("README.md", 'r') as f:
      long_description = f.read()

setup(name='ezplot9',
      version='0.0.2',
      packages=find_packages(),
      description='Package for quick plots',
      url='http://github.com/wkostelecki/ezplot9',
      author='Wojtek Kostelecki',
      install_requires=[
            'pandas',
            'numpy',
            'seaborn',
            'plotnine',
            'pydataset',
            'pytest',
            'bootstrapped'],
      license='MIT')


