FROM ubuntu:22.04

# Set environment variable to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    python3 \
    python3-dev \
    python3.10-venv \
    libmysqlclient-dev \
    openjdk-17-jdk \
    adb \
    pkg-config \
    aapt \
    build-essential \
    libjpeg-dev \
    libssl-dev \
    zlib1g-dev \
    tzdata \
    docker-compose \
    docker.io \
    && echo "tzdata tzdata/Areas select Etc" | debconf-set-selections && \
    echo "tzdata tzdata/Zones/Etc select UTC" | debconf-set-selections && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Node Version Manager (NVM) and Node.js 18.x
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash \
    && export NVM_DIR="$HOME/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && nvm install 18 \
    && nvm alias default 18 \
    && nvm use default \
    && npm install -g npm@latest \
    && npm install -g appium

# Install nvm
ENV NVM_DIR /root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash \
    && bash -c "source $NVM_DIR/nvm.sh && nvm install --lts && nvm alias default lts/*" \
    && rm -rf $NVM_DIR/.cache/src/* \



# Set environment variables for Java & Android SDK
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/emulator

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app


# Install any needed packages specified in requirements.txt
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel
RUN /opt/venv/bin/pip install -r requirements.txt

# Expose necessary ports
EXPOSE 4723 5554 5555 5900 8000

# Start services in the VNC session
CMD ["bash", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
