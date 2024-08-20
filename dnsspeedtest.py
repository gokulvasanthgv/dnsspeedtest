import dns.resolver
import time
import csv
import os
from datetime import datetime

# Read domains and DNS servers from files
with open('domains.txt', 'r') as f:
    domains = [line.strip().split(' - ') for line in f.readlines()]

with open('dnsserver.txt', 'r') as f:
    dns_servers = [line.strip().split(' - ') for line in f.readlines()]

# Ensure the format is correct and handle missing names/aliases
domains = [(d[0], d[1] if len(d) > 1 else f"custom{index+1}") for index, d in enumerate(domains)]
dns_servers = [(s[0], s[1] if len(s) > 1 else f"custom{index+1}") for index, s in enumerate(dns_servers)]

# Extract IP addresses and names
domain_addresses = [domain[0] for domain in domains]
domain_aliases = [domain[1] for domain in domains]
dns_ips = [server[0] for server in dns_servers]
dns_names = [server[1] for server in dns_servers]

# Initialize table header
header = ["DNS Server"] + domain_aliases + ["Average"]
print(f"{'DNS Server':<12}" + "".join([f"{alias:<20}" for alias in domain_aliases]) + f"{'Average':<20}")
print("=" * (12 + 20 * (len(domain_aliases) + 1)))

# Dictionary to store latencies
latencies = {name: [] for name in dns_names}

# List to store CSV rows
csv_rows = []

# Query each DNS server for each domain
for ip, name in zip(dns_ips, dns_names):
    row = [name]
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [ip]
    for domain in domain_addresses:
        start_time = time.perf_counter()
        try:
            resolver.resolve(domain)
            latency = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
            row.append(f"{latency:.3f}")
            latencies[name].append(latency)
        except Exception as e:
            row.append("Failed")
            latencies[name].append(None)
    
    # Calculate average latency
    valid_times = [t for t in latencies[name] if t is not None]
    if valid_times:
        avg_latency = sum(valid_times) / len(valid_times)
        row.append(f"{avg_latency:.3f}")
    else:
        row.append("No valid responses")
    
    print(f"{name:<12}" + "".join([f"{item:<20}" for item in row[1:]]))
    csv_rows.append(row)

# Get current date and time
current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# Write to CSV file
file_exists = os.path.isfile('speedtest.csv')

with open('speedtest.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    if not file_exists:
        writer.writerow(header)  # Write header only if file does not exist
    else:
        writer.writerow([])  # Add an empty row
        writer.writerow([])  # Add another empty row
        writer.writerow(header)  # Add domain aliases row in subsequent runs
    writer.writerow([f"Date and Time: {current_datetime}"])
    writer.writerows(csv_rows)
