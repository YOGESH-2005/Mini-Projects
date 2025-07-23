import socket
import threading
from queue import Queue
import json

# Common port-service mapping
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
    3306: 'MySQL', 3389: 'RDP'
}

print_lock = threading.Lock()
queue = Queue()

# Collect scan results
scan_results = []

# Function to scan a single port with retries and banner grabbing
def scan_port(ip, port, timeout, retries):
    for attempt in range(retries):
        try:
            sock = socket.socket()
            sock.settimeout(timeout)
            sock.connect((ip, port))
            try:
                banner = sock.recv(1024).decode(errors='ignore').strip()
            except:
                banner = "No banner"
            service = COMMON_PORTS.get(port, 'Unknown')
            with print_lock:
                print(f"[OPEN]   {ip}:{port} ({service}) - Banner: {banner}")
            scan_results.append({
                'ip': ip,
                'port': port,
                'service': service,
                'banner': banner,
                'status': 'open'
            })
            sock.close()
            break
        except:
            if attempt == retries - 1:
                with print_lock:
                    print(f"[CLOSED] {ip}:{port}")
                scan_results.append({
                    'ip': ip,
                    'port': port,
                    'service': COMMON_PORTS.get(port, 'Unknown'),
                    'banner': '',
                    'status': 'closed'
                })

# Worker thread function
def worker(ip, timeout, retries):
    while True:
        port = queue.get()
        scan_port(ip, port, timeout, retries)
        queue.task_done()

# Main program
def main():
    print("🔍 Python Port Scanner With Banner Grabing)\n")

    ips_input = input("Enter target IP addresses : ")
    ips = [ip.strip() for ip in ips_input.split(',') if ip.strip()]
    start_port = int(input("Enter start port: "))
    end_port = int(input("Enter end port: "))
    thread_count = int(input("Enter number of threads: "))
    timeout = float(input("Enter timeout per connection (in seconds): "))
    retries = int(input("Enter number of retries per port: "))

    for ip in ips:
        print(f"\n🔄 Scanning {ip} from port {start_port} to {end_port}...\n")
        
        # Start thread workers
        for _ in range(thread_count):
            t = threading.Thread(target=worker, args=(ip, timeout, retries))
            t.daemon = True
            t.start()

        # Queue up ports for scanning
        for port in range(start_port, end_port + 1):
            queue.put(port)

        queue.join()
        print(f"\n✅ Scan complete for {ip}.\n")

    # Save output to file
    with open("scan_results.json", "w") as f:
        json.dump(scan_results, f, indent=4)

    print("📁 Results saved to 'scan_results.json'")
    print("\n🔧 Built by YOGESH")

if __name__ == "__main__":
    main()
