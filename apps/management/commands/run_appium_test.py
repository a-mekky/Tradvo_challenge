import os
import subprocess
from time import sleep
import time
from django.core.management.base import BaseCommand
from appium import webdriver
from apps.models import App
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import signal
import docker


class Command(BaseCommand):
    help = 'Run Appium tests on an uploaded APK'

    def add_arguments(self, parser):
        parser.add_argument('app_id', type=int, help='The ID of the app to test')

    def wait_for_emulator_boot(self, app_id, ip_address):
        max_wait = 120  # Maximum wait time in seconds
        start_time = time.time()
        container_name = f'android_emulator_{app_id}'
        while time.time() - start_time < max_wait:
            try:
                result = subprocess.run(
                    ['docker', 'exec', container_name, 'adb', 'shell', 'getprop', 'sys.boot_completed'],
                    capture_output=True, text=True, check=True
                )
                if result.stdout.strip() == '1':
                    self.stdout.write(self.style.SUCCESS('Emulator fully booted.'))
                    self.stdout.write(self.style.SUCCESS('Emulator fully booted.'))
                    connect_result = subprocess.run(['adb', 'connect', f'{ip_address}:5555'], capture_output=True, text=True)
                    self.stdout.write(self.style.SUCCESS(f"Connected to ADB server: {connect_result.stdout.strip()}"))

                    return
            except subprocess.CalledProcessError:
                pass
            sleep(5)
        self.stderr.write(self.style.WARNING('Emulator boot timed out. Proceeding anyway.'))

    def start_emulator_and_appium(self, app_id):
        try:
            client = docker.from_env()

            container_name = f'android_emulator_{app_id}'

            env = {
                'DEVICE': 'Samsung Galaxy S10',
                'WEB_VNC': 'true',
                'APPIUM': 'true',
            }

            ports = {
                '5554/tcp': None,
                '5555/tcp': None,
                '4723/tcp': None,
                '6080/tcp': None,
            }

            volumes = {
                'app_manager_shared-data': {'bind': '/app/media', 'mode': 'rw'},
                '/dev/kvm': {'bind': '/dev/kvm', 'mode': 'rw'},
            }

            container = client.containers.run(
                'budtmo/docker-android:emulator_11.0',
                detach=True,
                environment=env,
                ports=ports,
                volumes=volumes,
                privileged=True,
                network='app_manager_default',
                name=container_name
            )

            # Retrieve the assigned ports
            container.reload()
            ip_address = container.attrs['NetworkSettings']['Networks']['app_manager_default']['IPAddress']
            assigned_ports = container.attrs['NetworkSettings']['Ports']
            appium_port = int(assigned_ports['4723/tcp'][0]['HostPort'])

            self.stdout.write(self.style.SUCCESS(f'Android Emulator (ID: {app_id}) started. Appium port: {appium_port}'))
            # Wait for the emulator to be fully booted
            self.wait_for_emulator_boot(app_id, ip_address)

            return ip_address

        except docker.errors.APIError as e:
            self.stderr.write(self.style.ERROR(f"Error starting the emulator and Appium server: {e}"))
            return False
        return True

    def stop_emulator_and_appium(self, app_id):
        try:
            client = docker.from_env()
            container = client.containers.get(f'android_emulator_{app_id}')
            container.stop()
            container.remove()
            self.stdout.write(
                self.style.SUCCESS(f'Android Emulator (ID: {app_id}) and Appium server stopped and removed.'))
        except docker.errors.NotFound:
            self.stderr.write(
                self.style.WARNING(f"Container for app_id {app_id} not found. It may have already been removed."))
        except docker.errors.APIError as e:
            self.stderr.write(self.style.ERROR(f"Error stopping the emulator and Appium server: {e}"))

    def verify_file_in_container(self, app_id, file_path):
        container_name = f'android_emulator_{app_id}'
        try:
            result = subprocess.run(['docker', 'exec', container_name, 'ls', file_path],
                                    capture_output=True, text=True, check=True)
            self.stdout.write(self.style.SUCCESS(f"File {file_path} exists in the container."))
            return True
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"File {file_path} not found in the container: {e.stderr}"))
            return False

    def install_apk(self, app_id, apk_path):
        container_name = f'android_emulator_{app_id}'
        try:
            # Use the same path as in the Django container, since we've mounted it at the same location
            result = subprocess.run(['docker', 'exec', container_name, 'adb', 'install', '-r', apk_path],
                                    capture_output=True, text=True, check=True)
            self.stdout.write(self.style.SUCCESS(f"APK installation output: {result.stdout}"))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Failed to install APK: {e}"))
            self.stderr.write(self.style.ERROR(f"Error output: {e.stderr}"))
            return False
        return True

    def get_package_and_activity(self, apk_path):
        try:
            result = subprocess.run(['aapt', 'dump', 'badging', apk_path], capture_output=True, text=True)
            package = None
            activity = None
            for line in result.stdout.split('\n'):
                if line.startswith('package:'):
                    package = line.split("name='")[1].split("'")[0]
                elif line.startswith('launchable-activity:'):
                    activity = line.split("name='")[1].split("'")[0]
            if not package or not activity:
                raise ValueError("Could not extract package name or main activity")
            return package, activity
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error getting package and activity: {e}"))
            return None, None

    def handle(self, *args, **options):
        after_click_ui_hierarchy = None
        screen_changed = 'no'
        app_id = None
        try:
            app_id = options['app_id']
            app = App.objects.get(id=app_id)

            self.stdout.write(self.style.SUCCESS(f"Starting test for app: {app.name} (ID: {app_id})"))

            ip_address = self.start_emulator_and_appium(app_id)
            if not ip_address:
                self.stderr.write(self.style.ERROR("Failed to start emulator and Appium"))
                return

            # Use a sanitized version of the app name for file names
            safe_app_name = app.name.replace(' ', '_')

            app_apk_path = os.path.join('/app/media', app.apk_file_path.name)

            if not os.path.isfile(app_apk_path):
                self.stderr.write(self.style.ERROR(f"APK file not found at: {app_apk_path}"))
                return

            if not self.verify_file_in_container(app_id, app_apk_path):
                self.stderr.write(self.style.ERROR("APK file not accessible in the Android emulator container"))
                return

            if not self.install_apk(app_id, app_apk_path):
                self.stderr.write(self.style.ERROR("Failed to install APK"))
                return

            package_name, main_activity = self.get_package_and_activity(app_apk_path)
            if not package_name or not main_activity:
                self.stderr.write(self.style.ERROR("Failed to get package name or main activity"))
                return

            first_screenshot_path = os.path.join('/app/media', 'screenshots', f'{safe_app_name}_first.png')
            second_screenshot_path = os.path.join('/app/media', 'screenshots', f'{safe_app_name}_second.png')
            video_path = f'/sdcard/{safe_app_name}_test.mp4'

            self.stdout.write(self.style.SUCCESS('Starting screen recording...'))
            recording_process = subprocess.Popen(['adb', 'shell', 'screenrecord', video_path], start_new_session=True)

            capabilities = {
                'platformName': 'Android',
                'automationName': 'UiAutomator2',
                'deviceName': f'emulator-{5554 + app_id}',
                'appPackage': package_name,
                'appActivity': main_activity,
                'language': 'en',
                'locale': 'US',
                'adbExecTimeout': 120000,
                'noReset': False
            }

            driver_options = UiAutomator2Options().load_capabilities(capabilities)
            driver = None

            try:
                appium_port = 4723
                self.stdout.write(self.style.SUCCESS('Before Connected to Appium...'))
                driver = webdriver.Remote(f'http://{ip_address}:{appium_port}', options=driver_options)
                wait = WebDriverWait(driver, 20)
                self.stdout.write(self.style.SUCCESS('Connected to Appium...'))

                wait.until(EC.presence_of_element_located((AppiumBy.CLASS_NAME, 'android.widget.TextView')))

                initial_ui_hierarchy = driver.page_source
                driver.save_screenshot(first_screenshot_path)
                self.stdout.write(self.style.SUCCESS('first screenshot taken...'))

                after_click_ui_hierarchy = initial_ui_hierarchy
                try:
                    first_clickable = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//*[@clickable='true']")))
                    first_clickable.click()
                    self.stdout.write(self.style.SUCCESS('clicked...'))
                    sleep(2)
                    after_click_ui_hierarchy = driver.page_source
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error clicking the first element: {e}'))

                driver.save_screenshot(second_screenshot_path)
                self.stdout.write(self.style.SUCCESS('second screenshot taken...'))

                # Determine if the screen has changed
                screen_changed = screen_changed = 'yes' if initial_ui_hierarchy != after_click_ui_hierarchy else 'no'
                self.stdout.write(self.style.SUCCESS('screen changed...'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error during test execution: {e}"))
            finally:
                if driver:
                    driver.quit()

                # Stop recording (executed on Android Emulator container) and ensure the process is fully terminated
                self.stdout.write('Stopping screen recording...')
                subprocess.run(['adb', 'shell', 'killall', '-INT', 'screenrecord'])
                sleep(5)  # Wait for the recording to finish

                # Pull the video from the emulator (executed on Android Emulator container)
                subprocess.run(['adb', 'pull', '/sdcard/test.mp4', video_path])
                recording_process.send_signal(signal.SIGINT)  # Terminate the screen recording process
                recording_process.wait()  # Wait for the process to terminate

                # Ensure the emulator has completed writing the video file
                sleep(5)
                # Pull the video from the emulator to the local machine
                self.stdout.write('Pulling video from emulator...')
                local_video_dir = 'media/videos'
                local_video_path = os.path.join(local_video_dir, f'{safe_app_name}_test.mp4')

                # Ensure the local video directory exists
                os.makedirs(local_video_dir, exist_ok=True)

                video_pull_command = ['adb', 'pull', video_path, local_video_path]
                try:
                    subprocess.run(video_pull_command, check=True)
                except subprocess.CalledProcessError as e:
                    self.stderr.write(self.style.ERROR(f"Error pulling video: {e}"))
                    self.stderr.write(self.style.ERROR(f"Error output: {e.stderr.decode()}"))

                local_video_path = os.path.join('media/videos', f'{app.name}_test.mp4')
                if os.path.exists(local_video_path):
                    self.stdout.write(self.style.SUCCESS(f"Video pulled successfully: {local_video_path}"))
                else:
                    self.stderr.write(self.style.ERROR("Video pull failed: File does not exist."))

                app.first_screen_screenshot_path = os.path.join('screenshots', f'{safe_app_name}_first.png')
                app.second_screen_screenshot_path = os.path.join('screenshots', f'{safe_app_name}_second.png')
                app.video_recording_path = os.path.join('videos', f'{safe_app_name}_test.mp4')
                app.ui_hierarchy = after_click_ui_hierarchy
                app.screen_changed = screen_changed
                app.save()

            self.stdout.write(self.style.SUCCESS('Test completed.'))
            self.stop_emulator_and_appium(app_id)
            self.stdout.write(self.style.SUCCESS("Test completed successfully."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during test execution: {e}"))
            self.stop_emulator_and_appium(app_id)
            self.stderr.write(self.style.ERROR(f"Error during test execution: {e}"))