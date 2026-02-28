FROM mambaorg/micromamba:1.5.8-jammy

# Create a fixed environment (reproducible base)
# Packages from conda-forge: python, 4ti2, normaliz, coreutils for sha256sum
RUN micromamba install -y -n base -c conda-forge \
    python=3.11 \
    4ti2 \
    normaliz \
    coreutils \
 && micromamba clean -a -y

# Copy helper scripts into image (not overridden by volume mount)
COPY --chmod=755 run.sh /usr/local/bin/run.sh
COPY make_normaliz_input.py /usr/local/bin/make_normaliz_input.py

ENV PATH="/opt/conda/bin:${PATH}"
WORKDIR /work
ENTRYPOINT ["/opt/conda/bin/bash", "/usr/local/bin/run.sh"]