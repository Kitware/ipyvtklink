import pyvista
import vtk

def screenshot(render_window, transparent_background=False):
    """Helper to fetch screenshot of render window."""
    ifilter = vtk.vtkWindowToImageFilter()
    ifilter.SetInput(render_window)
    ifilter.ReadFrontBufferOff()
    if transparent_background:
        ifilter.SetInputBufferTypeToRGBA()
    else:
        ifilter.SetInputBufferTypeToRGB()
    ifilter.Modified()
    ifilter.Update()
    image = pyvista.wrap(ifilter.GetOutput())
    img_size = image.dimensions
    img_array = pyvista.utilities.point_array(image, 'ImageScalars')
    # Reshape and write
    tgt_size = (img_size[1], img_size[0], -1)
    return img_array.reshape(tgt_size)[::-1]
