FROM python:3.11-slim

WORKDIR /monitor

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY monitor.py .
COPY config.example.env .

# If you want the container to be able to reboot the host, run as root (NOT recommended for production).
# To allow reboot from container, you'll also need to provide appropriate sudoers and privileges on the host.

CMD ["python", "monitor.py"]