```markdown
# Website Monitoring and Recovery (sample project)

Overview
- This sample project demonstrates a small website + monitor system.
- The app service is a simple Flask app (sample application).
- The monitor service checks the app (or any website URL), sends email alerts when the site is down, and tries to restart the application container. If restarts fail repeatedly, it can optionally reboot the host.

Technologies
- Python 3 (Flask app, monitoring scripts)
- Docker & Docker Compose
- Linux (server bootstrap script provided)
- SMTP for email notifications (configure credentials as environment variables)

Repository layout
- docker-compose.yml
- app/
  - Dockerfile
  - app.py
  - requirements.txt
- monitor/
  - Dockerfile
  - monitor.py
  - requirements.txt
  - config.example.env
- ec2/
  - user-data.sh
- .gitignore

Quick local run (recommended for testing)
1. Clone repo locally.
2. Copy `monitor/config.example.env` to `monitor/.env` and edit the variables, especially SMTP credentials and TARGET_URL.
3. From repository root:
   - docker compose up --build -d
   - The app service is accessible on http://localhost:8000 (if you mapped ports).
   - The monitor will check TARGET_URL. Check logs: docker compose logs -f monitor

What the monitor does
- Periodically polls TARGET_URL.
- If it sees failures (non-200 responses or exceptions) it increments a failure counter.
- Once failures >= FAILURE_THRESHOLD it:
  - Sends alert email to ALERT_TO.
  - Attempts to restart the target container (CONTAINER_NAME) using the Docker socket.
  - If container restart fails after RETRY_RESTART times, optionally issues a host reboot (requires monitor container to have permission to reboot the host; use with care).

Security / Notes
- You must provide SMTP credentials. For Gmail, use an App Password and TLS (recommended).
- Mounting the Docker socket inside the monitor container gives it control over Docker on the host. This is powerful and potentially dangerous — only do this on trusted hosts.
- Rebooting the host from a container may require running with extra privileges (or sudo access). A safer option is to rely only on container restarts.

Deploy to AWS EC2 (high-level)
1. Create an EC2 instance (Ubuntu 22.04 recommended).
2. Allow ports: 22 (SSH), 8000 (app) and any other you need. For public testing, open 8000 to your IP or all if explicit.
3. Use the provided `ec2/user-data.sh` as user-data (update the GIT_REPO placeholder to your repo URL).
4. When instance boots it will:
   - Install docker, docker-compose.
   - Clone your repo.
   - Run `docker compose up -d`.
5. Set monitor environment variables (either via file inside monitor/.env on instance or exported in systemd / env file).

Files included are examples and templates — replace placeholders (YOUR_EMAIL, SMTP credentials, your GitHub repo URL) before running.