from functools import wraps

import pyvista

from .viewer import ViewInteractiveWidget


class iPlotter(pyvista.Plotter):
    """Wrapping of PyVista's Plotter to be used interactively in Jupyter."""

    def __init__(self, *args, **kwargs):
        transparent_background = kwargs.pop('transparent_background', pyvista.rcParams['transparent_background'])
        kwargs["notebook"] = False
        kwargs["off_screen"] = False
        pyvista.Plotter.__init__(self, *args, **kwargs)
        self.ren_win.SetOffScreenRendering(1)
        self.off_screen = True
        self._widget = ViewInteractiveWidget(self.ren_win, transparent_background=transparent_background)


    @wraps(pyvista.Plotter.show)
    def show(self, *args, **kwargs):
        kwargs["auto_close"] = False
        _ = pyvista.Plotter.show(self, *args, **kwargs) # Incase the user sets the cpos or something
        return self.widget

    @property
    def widget(self):
        self._widget.full_render()
        return self._widget
