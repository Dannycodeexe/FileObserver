# File Observer & Security Audit System

An automated, background-running system monitoring utility built with Python that tracks high-risk Windows directories, denounces high-frequency events, and securely archives summary reports to cloud storage while sending real-time email alerts.

## What This Project has
- **Event-Driven File System Monitoring:** Uses the `watchdog` library to observe critical OS directories (`Downloads`, `AppData\Local\Temp`, `Startup`, and `AppData\Roaming`) with top-level scoping (`recursive=False`) to eliminate background noise.
- **Asynchronous Event Debouncing:** Implements thread-safe collection queues and a countdown timer (`threading.Timer`) to aggregate rapid file bursts into single consolidated batches.
- **Cloud Automation & Local Privacy:** Intercepts large binaries or executables locally and instead generates structured `.txt` summary logs, uploading them directly to Dropbox via the Dropbox API.
- **Secure Network Communications:** Handles direct SSL socket connections (`smtplib.SMTP_SSL` on port 465) with custom header sanitization to prevent SMTP injection and newline errors.

## Requirements
Look at the requirment.text file to see what is needed!

## The Environment
I made my .env file look like this for this project

````
# Access Token
DROPBOX_ACCESS_TOKEN=sl.u.FAKE_TOKEN_EXAMPLE_ABC123XYZ789_DEMO_PURPOSES_ONLY

# Email Alert Credentials (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=abcd1234efgh5678
RECIPIENT_EMAIL=your_email@gmail.com
````
