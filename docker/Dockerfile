# Base image with CUDA + LeRobot runtime
FROM huggingface/lerobot-gpu@sha256:da85358de50c2ad135d54628e8b92a69a24eb9fe2b518f2d0d82c97a25b3f709

USER root

# Use bash so we can source the virtual environment in RUN commands
SHELL ["/bin/bash", "-lc"]

ARG FLASH_ATTN_WHL="https://github.com/lesj0610/flash-attention/releases/download/v2.8.3-cu12-torch2.10-cp312/flash_attn-2.8.3%2Bcu12torch2.10cxx11abiTRUE-cp312-cp312-linux_x86_64.whl"

# Install python packages
RUN source /lerobot/.venv/bin/activate && \
    uv pip install --no-deps "${FLASH_ATTN_WHL}" && \
    uv pip install --no-build-isolation "lerobot[groot,reachy2]"

WORKDIR /lerobot

# Keep the container interactive by default
CMD ["bash"]
