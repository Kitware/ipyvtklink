FROM continuumio/miniconda3 AS conda
SHELL ["/bin/bash", "-c"]

USER root

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

WORKDIR /root
COPY . ./ipyvtk/
WORKDIR /root/ipyvtk

RUN pip install .

COPY start.sh /sbin/start_xvfb.sh
RUN chmod a+x /sbin/start_xvfb.sh

ENTRYPOINT ["tini", "-g", "--", "start_xvfb.sh"]
# CMD ["/bin/bash"]
CMD ["jupyter", "notebook", "--port=8877", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
