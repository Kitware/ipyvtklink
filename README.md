# ipyvtk_simple

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Kitware/ipyvtk-simple/master)
[![PyPI](https://img.shields.io/pypi/v/ipyvtk_simple.svg?logo=python&logoColor=white)](https://pypi.org/project/ipyvtk_simple/)

*An ipywidget for vtkRenderWindow*

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
simply its installation in virtual environments where vtk may be built from
source or bundled with ParaView and we do not want to install the wheels from
PyPI.

## Run in Docker

To build and run in Docker:

```
docker build -t ipyvtk_simple .
docker run -p 8877:8877 ipyvtk_simple jupyter notebook --port=8877 --no-browser --ip=0.0.0.0 --allow-root
```

and open the `pyvista.ipynb` notebook.

Additionally, this can be used with ParaView. An example is given in
`paraview.ipynb` which can be run via:

```
docker build -t ipyvtk_pv -f paraview.dockerfile .
docker run -p 8877:8877 ipyvtk_pv jupyter notebook --port=8877 --no-browser --ip=0.0.0.0 --allow-root
```

and open the `paraview.ipynb` notebook.

## Examples

You may have to build jupyter lab extensions for this to work in Lab. This is
known to work well in Notebook.


### PyVista

PyVista is working to implement this in [a pull request](https://github.com/pyvista/pyvista/pull/824).
See the `pyvista.ipynb` for a proof of concept.


![demo-1](https://raw.githubusercontent.com/Kitware/ipyvtk-simple/master/assets/demo-1.gif)

![demo-2](https://raw.githubusercontent.com/Kitware/ipyvtk-simple/master/assets/demo-2.gif)


### Python VTK

The widget here can be used with VTK. Here is a minimal example showing how
to pass any `vtkRenderWindow` to the `ViewInteractiveWidget`:

```py
import vtk
from ipyvtk_simple.viewer import ViewInteractiveWidget

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

![demo-3](https://raw.githubusercontent.com/Kitware/ipyvtk-simple/master/assets/demo-3.gif)


### ParaView Python

See instructions above for running ParaView in a Docker container.

```py
import paraview.simple as pvs
from ipyvtk_simple.viewer import ViewInteractiveWidget

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

![demo-4](https://raw.githubusercontent.com/Kitware/ipyvtk-simple/master/assets/demo-4.gif)
