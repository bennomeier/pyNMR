from setuptools import setup

with open('README.org') as f:
    long_description = f.read()

setup(name='pynmr',
      version='0.25',
      description='Parse and Process NMR data.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=['License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: Physics'],
      keywords='pynmr NMR TopSpin RS2D NTNMR Magritek',
      url='http://github.com/bennomeier/pyNMR',
      author='Benno Meier',
      author_email='meier.benno@gmail.com',
      license='MIT',
      packages=['pyNMR'],
      include_package_data=True,
            install_requires = [
          'numpy',
          'spindata',
                'scipy',
                'paramiko',
                'pyqtgraph',
                'PyQt5',
                'BeautifulSoup4',
                'spindata',
          ],
      zip_safe=False)

