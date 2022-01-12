# ipyvtklink

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Kitware/ipyvtklink/master)
[![PyPI](https://img.shields.io/pypi/v/ipyvtklink.svg?logo=python&logoColor=white)](https://pypi.org/project/ipyvtklink/)
[![conda](https://img.shields.io/conda/vn/conda-forge/ipyvtklink.svg?logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/ipyvtklink)

*An ipywidget for vtkRenderWindow* (formerly `ipyvtk-simple`)

This is an early prototype of creating a Jupyter interface to VTK. This toolkit
is a proof of concept and a more polished tool will be available as
[`ipyvtk`](https://github.com/Kitware/ipyvtk) in the future.

The code here was implemented from the work done by [Andras Lasso](https://github.com/lassoan)
under an MIT License (see [the source](https://github.com/Slicer/SlicerJupyter/blob/master/JupyterNotebooks/JupyterNotebooksLib/interactive_view_widget.py)).

The goal is to enable this widget to work with any server side
[`vtkRenderWindow`](https://vtk.org/doc/nightly/html/classvtkRenderWindow.html)
This render window could be from [VTK Python](https://vtk.org/),
[ParaView](https://www.paraview.org/), or [PyVista](https://www.pyvista.org/).

Please note that `vtk` is not listed as a requirement for this package to
simplify its installation in virtual environments where VTK may be built from
source or bundled with ParaView and we do not want to install the wheels from
PyPI.

## Installation

For use with PyVista, simply install with `pip` or `conda`:

```
pip install ipyvtklink
```

or
```
conda install -c conda-forge ipyvtklink
```

## Run in Docker

A Docker image is prebuilt and hosted in the ipyvtklink repository's packages.

To run in Docker:

```
docker pull ghcr.io/kitware/ipyvtklink:latest
docker run -p 8888:8888 ghcr.io/kitware/ipyvtklink:latest
```

and open the `vtk.ipynb` notebook.

Additionally, this can be used with ParaView. An example is given in
`paraview.ipynb` which can be run via:

```
docker pull ghcr.io/kitware/ipyvtklink-paraview:latest
docker run -p 8878:8878 ghcr.io/kitware/ipyvtklink-paraview:latest
```

## Examples

You may have to build jupyter lab extensions for this to work in Lab. This is
known to work well in Notebook.


### PyVista

PyVista has fully implemented downstream support for `ipyvtklink`. See [PyVista's Documentation](https://docs.pyvista.org/user-guide/jupyter/ipyvtk_plotting.html)

See the `pyvista.ipynb` for an original proof of concept.

![demo-1](https://raw.githubusercontent.com/Kitware/ipyvtklink/master/assets/demo-1.gif)

![demo-2](https://raw.githubusercontent.com/Kitware/ipyvtklink/master/assets/demo-2.gif)


### Python VTK

The widget here can be used with VTK. Here is a minimal example showing how
to pass any `vtkRenderWindow` to the `ViewInteractiveWidget`:

```py
import vtk
from ipyvtklink.viewer import ViewInteractiveWidget

# Create some data
cylinder = vtk.vtkCylinderSource()
cylinder.SetResolution(8)
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cylinder.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Set up render window
ren = vtk.vtkRenderer()
ren_win = vtk.vtkRenderWindow()
ren_win.SetOffScreenRendering(1)
ren_win.SetSize(600, 600)
ren_win.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)
style = vtk.vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(style)

# Add actor to scene
ren.AddActor(actor)
ren.ResetCamera()

# Display
ViewInteractiveWidget(ren_win)
```

![demo-3](https://raw.githubusercontent.com/Kitware/ipyvtklink/master/assets/demo-3.gif)


### ParaView Python

See instructions above for running ParaView in a Docker container.

```py
import paraview.simple as pvs
from ipyvtklink.viewer import ViewInteractiveWidget

# Create data on the pipeline
wavelet = pvs.Wavelet()
contour = pvs.Contour(Input=wavelet)
contour.ContourBy = ['POINTS', 'RTData']
contour.Isosurfaces = [63, 143, 170, 197, 276]

# Set the data as visible
pvs.Show(contour)

# Fetch the view and render the scene
view = pvs.GetActiveView()
pvs.Render(view)

# Fetch the RenderWindow
ren_win = view.GetClientSideObject().GetRenderWindow()
# Display the RenderWindow with the widget
ViewInteractiveWidget(ren_win)
```

![demo-4](https://raw.githubusercontent.com/Kitware/ipyvtklink/master/assets/demo-4.gif)
