import argparse
import csv
import os
from datetime import datetime, timezone
import speedtest

def run_speedtest():
    s = speedtest.Speedtest()
    s.get_best_server()
    download_bps = s.download()
    upload_bps = s.upload(pre_allocate=False)
    results = s.results.dict()
    return {
        # use timezone-aware UTC to avoid DeprecationWarning
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "server_id": results.get("server", {}).get("id"),
        "server_name": results.get("server", {}).get("name"),
        "sponsor": results.get("server", {}).get("sponsor"),
        "country": results.get("server", {}).get("country"),
        "host": results.get("server", {}).get("host"),
        "lat": results.get("server", {}).get("lat"),
        "lon": results.get("server", {}).get("lon"),
        "ping_ms": results.get("ping"),
        "download_mbps": round(download_bps / 1_000_000, 3),
        "upload_mbps": round(upload_bps / 1_000_000, 3),
        "client_ip": results.get("client", {}).get("ip"),
        "client_isp": results.get("client", {}).get("isp"),
    }

def write_csv(path, row, fieldnames):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def choose_device_interactive(devices):
    while True:
        print("Select device:")
        for i, d in enumerate(devices, 1):
            print(f"{i}. {d}")
        sel = input("Enter number or name (leave empty for UNKNOWN): ").strip()
        if not sel:
            return "UNKNOWN"
        if sel.isdigit():
            idx = int(sel)
            if 1 <= idx <= len(devices):
                return devices[idx - 1]
        elif sel in devices:
            return sel
        print("Invalid selection, try again.")

def main():
    default_output = r"C:\logs\speedtest\speedtest_results.csv"
    devices = ["TUCMOTO5", "TUCMOTO2", "ZyXEL20522"]

    parser = argparse.ArgumentParser(description="Run speedtest and append results to CSV.")
    parser.add_argument("--output", "-o", default=default_output, help=f"CSV output path (default: {default_output})")
    parser.add_argument("--device", "-d", choices=devices, help="Device name to record (if omitted you'll be prompted)")
    args = parser.parse_args()

    if args.device:
        device = args.device
    else:
        device = choose_device_interactive(devices)

    try:
        row = run_speedtest()
    except Exception as e:
        print(f"Speedtest failed: {e}")
        return

    # add device as the first column
    row = {"device": device, **row}

    fieldnames = [
        "device", "timestamp", "server_id", "server_name", "sponsor", "country", "host", "lat", "lon",
        "ping_ms", "download_mbps", "upload_mbps", "client_ip", "client_isp"
    ]
    write_csv(args.output, row, fieldnames)
    print(f"Saved results to {os.path.abspath(args.output)}")
    print(f"Device: {device} — Download: {row['download_mbps']} Mbps, Upload: {row['upload_mbps']} Mbps, Ping: {row['ping_ms']} ms")

if __name__ == "__main__":
    main()