FROM ipyvtklink

# Have to uninstall VTK because ParaView bundles it's own
RUN conda uninstall --quiet --yes pyvista vtk
RUN conda install --quiet --yes -c conda-forge paraview=5.8.0


ENTRYPOINT ["tini", "-g", "--", "start_xvfb.sh"]
CMD ["/bin/bash"]
