FROM condaforge/miniforge3
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
    python=3.7 \
    'nodejs>=12.0.0' \
    'jupyterlab>=3' \
    'ipywidgets~=7.7' \
    'ipycanvas>=0.5.0' \
    'ipyevents>=0.8.0' \
    pillow \
    matplotlib \
    scipy \
    paraview=5.8.0
# NOTE ParaView bundles it's own VTK

WORKDIR $HOME
COPY . ./ipyvtklink/
WORKDIR $HOME/ipyvtklink

RUN pip install .

COPY start.sh /sbin/start_xvfb.sh
RUN chmod a+x /sbin/start_xvfb.sh

ENTRYPOINT ["tini", "-g", "--", "start_xvfb.sh"]
# CMD ["/bin/bash"]
CMD ["jupyter", "lab", "--port=8878", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
