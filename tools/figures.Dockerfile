FROM python:3.12.13-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36

# This image is the figure ABI: the base-image digest fixes Python and the
# Linux userspace, while requirements.txt fixes matplotlib, FreeType (bundled
# in its wheel), Pillow and NumPy.  Both local Make targets and CI build this
# same linux/amd64 image.
ENV AI_DISCOVERY_RENDERER=linux-amd64-python-3.12.13 \
    HOME=/tmp \
    MPLCONFIGDIR=/tmp/matplotlib \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt /tmp/ai-discovery-requirements.txt
RUN python -m pip install --disable-pip-version-check \
        --requirement /tmp/ai-discovery-requirements.txt

WORKDIR /repo
