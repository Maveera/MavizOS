FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y live-build rsync python3 python3-venv python3-pip && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY . /build
CMD ["bash", "install/bootguardai/iso/build-iso.sh"]
