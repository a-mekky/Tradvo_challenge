# Django and Appium Integration

## Overview

This project provides a setup for integrating Django with Appium for automated testing of Android APKs. It includes a Docker-based environment for running a Django application, a MySQL database, and an Android emulator. The setup also includes automated tests for user management and APK handling.

## Project Structure

- `Dockerfile`: Defines the Docker image for the Django application with dependencies.
- `docker-compose.yml`: Defines the multi-container setup including Django, MySQL, and Android emulator.
- `requirements.txt`: Lists Python dependencies for the Django project.
- `tests.py`: Contains test cases for user registration, login, app management, and Appium integration.
- `Accessibility.js`: JavaScript for accessibility features on the frontend.
- `README.md`: Documentation file.

## Getting Started

### Prerequisites

Ensure you have Docker and Docker Compose installed. Follow the installation steps below for your operating system.

### Installing Docker

#### On Linux (Ubuntu-based systems)

1. **Update package list:**

    ```bash
    sudo apt-get update
    ```

2. **Install dependencies:**

    ```bash
    sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
    ```

3. **Add Docker's GPG key:**

    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    ```

4. **Add Docker repository:**

    ```bash
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    ```

5. **Install Docker Engine:**

    ```bash
    sudo apt-get update
    sudo apt-get install docker-ce
    ```

6. **Install Docker Compose:**

    ```bash
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```

#### On Windows

1. **Download Docker Desktop for Windows:**

    Visit [Docker's official website](https://www.docker.com/products/docker-desktop) and download the installer.

2. **Run the installer and follow the prompts.**

3. **Start Docker Desktop from the Start menu.**

## Running the Application

1. **Clone the repository:**

    ```bash
    git clone https://github.com/a-mekky/Tradvo_challenge.git
    cd Tradvo_challenge
    ```

2. **Build and start the containers:**

    ```bash
    docker-compose up --build
    ```

3. **Access the web application:**

    Open your browser and go to `http://localhost:8000` to access the Django application.

4. **Open a shell inside the web container:**

    ```bash
    docker-compose exec web /bin/bash
    ```

5. **Run Django tests:**

    Inside the web container, execute the following command to run tests:

    ```bash
    python manage.py test
    ```

## Features

### Accessibility

- **High Contrast Mode:** Toggle high contrast mode for better visibility.
- **Font Size Adjustment:** Select different font sizes for accessibility.

### Multilingual Support

- **Language Switch:** Option to switch between English and French languages. Users can select their preferred language, and the application will dynamically update to reflect the selected language.


### Automated Testing

- **User Management Tests:** Includes registration, login, and user-related actions.
- **App Management Tests:** Tests for adding, editing, listing, and deleting apps.
- **Appium Integration Test:** Tests the ability to run Appium tests on uploaded APKs.

## Tests

### Test Cases

1. **User Registration Test:**

    Tests the registration of a new user and verifies the redirection and user creation.

2. **User Login Test:**

    Tests the login functionality and ensures the user session is created.

3. **App Add Test:**

    Tests adding a new app and verifies successful upload and app creation.

4. **App Edit Test:**

    Tests editing an existing app and verifies the updates are applied.

5. **List Apps Test:**

    Tests the listing of apps to ensure correct filtering based on the user.

6. **Delete App Test:**

    Tests the deletion of an app and verifies the app is removed.

7. **Appium Test:**

    Tests the integration with Appium to run automated tests on APKs.

## Future Updates

- Planned updates include the ability to run multiple tests simultaneously in separate containers, which will enhance test coverage and execution efficiency.
- Enhance error handling and container management
