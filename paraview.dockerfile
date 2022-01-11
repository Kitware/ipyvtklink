FROM continuumio/miniconda3 AS conda
MAINTAINER Bane Sullivan "bane.sullivan@kitware.com"
SHELL ["/bin/bash", "-c"]

ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-dev xvfb tini && \
    rm -rf /var/lib/apt/lists/*

RUN conda install --yes -c conda-forge \
    'nodejs>=12.0.0' \
    jupyterlab \
    ipywidgets \
    'ipycanvas>=0.5.0' \
    'ipyevents>=0.8.0' \
    pillow \
    pyvista \
    matplotlib \
    scipy

RUN jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    ipycanvas \
    ipyevents

RUN jupyter labextension enable \
    @jupyter-widgets/jupyterlab-manager \
    ipycanvas \
    ipyevents

WORKDIR $HOME
COPY . ./ipyvtklink/
WORKDIR $HOME/ipyvtklink

RUN pip install .

COPY start.sh /sbin/start_xvfb.sh
RUN chmod a+x /sbin/start_xvfb.sh

# Have to uninstall VTK because ParaView bundles it's own
RUN conda uninstall --quiet --yes pyvista vtk
RUN conda install --quiet --yes -c conda-forge paraview=5.8.0


ENTRYPOINT ["tini", "-g", "--", "start_xvfb.sh"]
CMD ["/bin/bash"]
# CMD ["jupyter", "notebook", "--port=8878", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
