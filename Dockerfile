FROM jupyter/base-notebook:python-3.9.7
MAINTAINER Bane Sullivan "bane.sullivan@kitware.com"

USER root
RUN apt-get update \
 && apt-get install  -yq --no-install-recommends \
    libfontconfig1 \
    libxrender1 \
    libosmesa6 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY setup.py /build-context/
COPY LICENSE /build-context/
COPY README.md /build-context/
COPY ipyvtklink /build-context/ipyvtklink
WORKDIR /build-context/
RUN pip install .

# Install PyVista's custom VTK wheel
RUN pip install https://github.com/pyvista/pyvista-wheels/raw/main/vtk-osmesa-9.1.0-cp39-cp39-linux_x86_64.whl

# allow jupyterlab for ipyvtk
ENV JUPYTER_ENABLE_LAB=yes
ENV PYVISTA_USE_IPYVTK=true

USER jovyan
WORKDIR $HOME
COPY vtk.ipynb $HOME/
