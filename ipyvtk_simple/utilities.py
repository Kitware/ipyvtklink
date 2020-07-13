"""Helper methods."""


def screenshot(render_window, transparent_background=False):
    """Helper to fetch screenshot of render window."""
    # Dynamic vtk import so we do not have to list vtk as a requirement
    #    this makes installing with ParaView very easy!
    import vtk
    import vtk.util.numpy_support as nps
    ifilter = vtk.vtkWindowToImageFilter()
    ifilter.SetInput(render_window)
    ifilter.ReadFrontBufferOff()
    if transparent_background:
        ifilter.SetInputBufferTypeToRGBA()
    else:
        ifilter.SetInputBufferTypeToRGB()
    ifilter.Modified()
    ifilter.Update()
    image = ifilter.GetOutput()
    img_size = image.GetDimensions()
    vtkarr = image.GetPointData().GetAbstractArray("ImageScalars")
    img_array = nps.vtk_to_numpy(vtkarr)
    # Reshape and write
    tgt_size = (img_size[1], img_size[0], -1)
    return img_array.reshape(tgt_size)[::-1]
