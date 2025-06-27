# Use a base image that's close to the GitHub Actions runner environment
FROM ubuntu:22.04 # Using 22.04 as it's a very stable LTS, 24.04 might still have quirks

LABEL maintainer="Your Name <marwannaili.23.07@gmail.com>"

# Set environment variables for non-interactive apt-get and locale
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    zip \
    unzip \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses-dev \
    cmake \
    libffi-dev \
    libssl-dev \
    curl \
    openjdk-17-jdk \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install buildozer cython

# Set up Android SDK and NDK environment variables
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_NDK_HOME=/opt/android-ndk-r25b
ENV PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_NDK_HOME

# Create directories for SDK and NDK
RUN mkdir -p $ANDROID_SDK_ROOT/cmdline-tools \
    && mkdir -p $ANDROID_NDK_HOME

# Download and install Android Command Line Tools
WORKDIR $ANDROID_SDK_ROOT/cmdline-tools
RUN curl -L -o tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip \
    && unzip tools.zip \
    && rm tools.zip \
    && mv cmdline-tools latest

# Download and install Android NDK (r25b)
WORKDIR $ANDROID_NDK_HOME
RUN curl -L -o ndk.zip https://dl.google.com/android/repository/android-ndk-r25b-linux.zip \
    && unzip ndk.zip \
    && rm ndk.zip \
    && mv android-ndk-r25b/* . \
    && rmdir android-ndk-r25b

# Accept Android SDK licenses
# This is crucial for non-interactive builds
RUN yes | $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --licenses

# Set working directory for the application code
WORKDIR /app

# Copy your application code (optional, can be done in workflow)
# COPY . /app

# Set default command (optional, buildozer will be run by workflow)
# CMD ["buildozer", "android", "debug"]
