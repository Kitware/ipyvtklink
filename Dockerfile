FROM continuumio/miniconda3 AS conda
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

RUN conda install --quiet --yes -c conda-forge \
    ipywidgets \
    ipycanvas \
    ipyevents \
    jupyter \
    ipython \
    pillow \
    pyvista \
    matplotlib \
    scipy

WORKDIR $HOME
COPY . ./ipyvtk/
WORKDIR $HOME/ipyvtk

RUN pip install .

COPY start.sh /sbin/start_xvfb.sh
RUN chmod a+x /sbin/start_xvfb.sh

ENTRYPOINT ["tini", "-g", "--", "start_xvfb.sh"]
CMD ["/bin/bash"]
# CMD ["jupyter", "notebook", "--port=8877", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
