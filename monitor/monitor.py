import os
import time
import smtplib
import socket
from email.message import EmailMessage
from dotenv import load_dotenv
import requests
import docker
import traceback

load_dotenv(dotenv_path="./monitor/.env" if os.path.exists("./monitor/.env") else None)

TARGET_URL = os.getenv("TARGET_URL", "http://app:8000/health")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 15))
FAILURE_THRESHOLD = int(os.getenv("FAILURE_THRESHOLD", 3))
RETRY_RESTART = int(os.getenv("RETRY_RESTART", 2))
REBOOT_ON_FAILURE = os.getenv("REBOOT_ON_FAILURE", "false").lower() == "true"
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "sample_app")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
ALERT_FROM = os.getenv("ALERT_FROM")
ALERT_TO = os.getenv("ALERT_TO")

def send_email(subject: str, body: str):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and ALERT_FROM and ALERT_TO):
        print("Email configuration incomplete; skipping email.")
        return
    try:
        msg = EmailMessage()
        msg["From"] = ALERT_FROM
        msg["To"] = ALERT_TO
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        print("Alert email sent.")
    except Exception as e:
        print("Failed to send email:", e)

def restart_container(client, name):
    try:
        container = client.containers.get(name)
        print(f"Restarting container {name} (id={container.short_id})...")
        container.restart(timeout=10)
        print("Container restart command issued.")
        return True
    except docker.errors.NotFound:
        print(f"Container {name} not found.")
    except Exception as e:
        print("Error restarting container:", e)
        traceback.print_exc()
    return False

def reboot_host():
    # Caution: only do this if you explicitly want the container to be able to reboot the host.
    try:
        print("Attempting host reboot...")
        # This may require the container to run as root and have permission to reboot.
        os.system("sync && /sbin/reboot")
    except Exception as e:
        print("Failed to reboot host:", e)

def main():
    failure_count = 0
    client = None
    try:
        client = docker.DockerClient(base_url="unix://var/run/docker.sock")
    except Exception as e:
        print("Could not initialize Docker client. If you want container restart capability, mount /var/run/docker.sock into this container.")
        print("Docker client init error:", e)

    while True:
        try:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking {TARGET_URL} ...")
            resp = requests.get(TARGET_URL, timeout=10)
            status = resp.status_code
            if 200 <= status < 300:
                if failure_count != 0:
                    print("Website recovered.")
                    send_email("Website recovered", f"{TARGET_URL} is responding again (status {status}). Host: {socket.gethostname()}")
                failure_count = 0
            else:
                failure_count += 1
                print(f"Non-2xx response: {status} (failure #{failure_count})")
        except Exception as e:
            failure_count += 1
            print(f"Request error (failure #{failure_count}):", e)

        if failure_count >= FAILURE_THRESHOLD:
            msg = f"{TARGET_URL} has failed {failure_count} consecutive checks on host {socket.gethostname()}."
            print("Threshold exceeded:", msg)
            send_email("Website DOWN alert", msg)
            restarted = False
            # Try to restart the container RETRY_RESTART times
            for attempt in range(1, RETRY_RESTART + 1):
                print(f"Attempt {attempt} to restart container {CONTAINER_NAME}...")
                if client:
                    ok = restart_container(client, CONTAINER_NAME)
                    if ok:
                        # after restart, wait some time to allow recovery
                        print("Waiting 10s for app to recover...")
                        time.sleep(10)
                        # perform one quick check
                        try:
                            r = requests.get(TARGET_URL, timeout=10)
                            if 200 <= r.status_code < 300:
                                print("App recovered after restart.")
                                send_email("Website recovered after restart", f"{TARGET_URL} recovered after restart (status {r.status_code}).")
                                failure_count = 0
                                restarted = True
                                break
                            else:
                                print("Still non-2xx after restart:", r.status_code)
                        except Exception as e:
                            print("Error checking after restart:", e)
                else:
                    print("No Docker client available; cannot restart container.")
                time.sleep(5)
            if not restarted:
                print("Restart attempts failed.")
                if REBOOT_ON_FAILURE:
                    send_email("Host REBOOTING due to persistent failure", f"{TARGET_URL} did not recover; rebooting host {socket.gethostname()} now.")
                    reboot_host()
            # Wait some time before next check cycle to avoid tight loop after actions
            time.sleep(30)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()