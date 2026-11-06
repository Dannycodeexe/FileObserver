import os
import time
import threading
from pathlib import Path
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from notifier import send_realtime_alert
from cloud_storage import DropboxUploader

load_dotenv()

uploader = DropboxUploader()

IGNORED_EXTENSIONS = {'.tmp', '.log', '.bak', '.crdownload', '.part', '.dat'}
IGNORED_PREFIXES = ('~$', 'dat.LOG', 'TMP')

pending_events = {}
debounce_timer = None
DEBOUNCE_INTERVAL = 5.0
events_lock = threading.Lock()


def flush_batch():
    global pending_events, debounce_timer

    with events_lock:
        if not pending_events:
            return

        batch = pending_events.copy()
        pending_events.clear()
        debounce_timer = None

    print(f"\n⚡ Processing aggregated batch of {len(batch)} file event(s)...")

    timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S')
    filename_timestamp = time.strftime('%Y%m%d_%H%M%S')

    summary_lines = [
        f"Security Alert Summary - {timestamp_str}",
        f"Total File Events Detected: {len(batch)}",
        "=" * 50,
        ""
    ]

    for path, event_type in batch.items():
        summary_lines.append(f"Action: {event_type}")
        summary_lines.append(f"File Name: {os.path.basename(path)}")
        summary_lines.append(f"Full Path: {path}")
        summary_lines.append("-" * 30)

    batch_summary_text = "\n".join(summary_lines)

    try:
        send_realtime_alert(f"BATCH ({len(batch)} items)", batch_summary_text)
    except Exception as e:
        print(f"❌ Batch email dispatch error: {e}")

    report_filename = f"Alert_Report_{filename_timestamp}.txt"
    temp_report_path = os.path.join(os.getcwd(), report_filename)

    try:
        with open(temp_report_path, "w", encoding="utf-8") as f:
            f.write(batch_summary_text)

        print(f"☁️ Uploading summary report '{report_filename}' to Dropbox...")
        uploader.upload_file(temp_report_path)

    except Exception as e:
        print(f"❌ Failed to create/upload Dropbox report: {e}")

    finally:
        if os.path.exists(temp_report_path):
            os.remove(temp_report_path)


class SecurityEventHandler(FileSystemEventHandler):

    def _should_ignore(self, file_path):
        if os.path.isdir(file_path):
            return True

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        if ext in IGNORED_EXTENSIONS:
            return True

        if any(filename.startswith(prefix) for prefix in IGNORED_PREFIXES):
            return True

        return False

    def _enqueue_event(self, event_type, file_path):
        global debounce_timer

        if self._should_ignore(file_path):
            return

        with events_lock:
            pending_events[file_path] = event_type
            print(f"📌 Queued [{event_type}]: {os.path.basename(file_path)} (Batch size: {len(pending_events)})")

            if debounce_timer is not None:
                debounce_timer.cancel()

            debounce_timer = threading.Timer(DEBOUNCE_INTERVAL, flush_batch)
            debounce_timer.start()

    def on_created(self, event):
        self._enqueue_event("CREATED", event.src_path)

    def on_modified(self, event):
        self._enqueue_event("MODIFIED", event.src_path)


def start_monitoring(directories):
    event_handler = SecurityEventHandler()
    observer = Observer()

    active_paths = []
    for path_str in directories:
        if os.path.exists(path_str):
            observer.schedule(event_handler, path=path_str, recursive=False)
            active_paths.append(path_str)
            print(f"👁️ Monitoring active for: {path_str}")
        else:
            print(f"⚠️ Warning: Directory not found, skipping: {path_str}")

    if not active_paths:
        print("❌ No valid directories found to monitor. Exiting.")
        return

    observer.start()
    print(f"\n🚀 Security File Observer active across {len(active_paths)} directory target(s). Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping File Observer service...")
        observer.stop()

        if debounce_timer is not None:
            debounce_timer.cancel()
            flush_batch()

    observer.join()


if __name__ == "__main__":
    home = Path.home()

    downloads_path = str(home / "Downloads")
    local_temp_path = str(home / "AppData" / "Local" / "Temp")
    startup_path = str(
        home / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    )
    roaming_path = str(home / "AppData" / "Roaming")

    WATCH_DIRECTORIES = [
        downloads_path,
        local_temp_path,
        startup_path,
        roaming_path,
    ]

    start_monitoring(WATCH_DIRECTORIES)