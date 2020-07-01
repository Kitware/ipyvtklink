import os
from io import open as io_open
from setuptools import setup

package_name = 'ipyvtk_simple'

__version__ = None
filepath = os.path.dirname(__file__)
version_file = os.path.join(filepath, package_name, '_version.py')
with io_open(version_file, mode='r') as fd:
    exec(fd.read())

readme_file = os.path.join(filepath, 'README.md')

setup(
    name=package_name,
    packages=[package_name,],
    version=__version__,
    description='ipywidget for vtkRenderWindow and PyVista interactive plotter.',
    long_description=io_open(readme_file, encoding="utf-8").read(),
    author='Bane Sullivan',
    author_email='bane.sullivan@kitware.com',
    classifiers=[
        'Development Status :: 4 - Beta',
    ],

    url='https://github.com/Kitware/ipyvtk-simple',
    keywords='vtk plotting pyvista jupyter',
    python_requires='>=3.5.*',
    install_requires=['pyvista',
                      'ipycanvas',
                      'ipyevents',
                      'ipywidgets',
    ],

)
