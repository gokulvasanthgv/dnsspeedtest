import dns.resolver
import time
import os
from datetime import datetime
import openpyxl
from openpyxl import Workbook
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar, ttk
from tkinter import font as tkfont  # Importing the font module

# Default DNS servers and domains
default_dns_servers = [
    "1.1.1.1 - Cloudflare",
    "8.8.8.8 - Google",
    "9.9.9.9 - Quad9",
    "208.67.222.222 - OpenDNS",
    "94.140.14.14 - Adguard",
    "76.76.2.0 - CTRLD",
    "77.88.8.8 - Yandex",
    "134.195.4.2 - OpenNIC"
]

default_domains = [
    "google.com - Google",
    "facebook.com - FB",
    "amazon.com - Amazon",
    "wikipedia.org - Wikipedia",
    "twitter.com - Twitter/X",
    "x.com - X",
    "netflix.com - Netflix",
    "instagram.com - Insta",
    "cnn.com - CNN",
    "example.com - Example"
]

# Function to get user input for DNS servers and domains
def get_user_input(default_list, title):
    def on_ok():
        user_input = text.get("1.0", tk.END).strip()
        if user_input:
            result = [item.strip() for item in user_input.split("\n") if item.strip()]
            root.result = result
        else:
            root.result = default_list
        root.quit()
        root.destroy()

    root = tk.Tk()
    root.title(title)
    root.geometry("600x400")
    root.resizable(True, True)

    scrollbar = Scrollbar(root)
    scrollbar.grid(row=0, column=1, sticky='ns')

    text = Text(root, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text.grid(row=0, column=0, sticky='nsew')
    text.insert(tk.END, "\n".join(default_list))

    scrollbar.config(command=text.yview)

    button = tk.Button(root, text="OK", command=on_ok)
    button.grid(row=1, column=0, columnspan=2, pady=10)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.result = None
    root.mainloop()
    return root.result

# Function to read DNS servers and domains from files
def read_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Function to save results to an Excel file
def save_to_excel(header, rows):
    # Get current date and time
    current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Write to Excel file
    file_exists = os.path.isfile('speedtest.xlsx')

    if file_exists:
        wb = openpyxl.load_workbook('speedtest.xlsx')
    else:
        wb = Workbook()

    ws = wb.active
    ws.append([f"Date and Time: {current_datetime}"])
    ws.append(header)

    for row in rows:
        ws.append(row)

    wb.save('speedtest.xlsx')

# Function to display the results in a GUI window
def display_results(header, rows):
    root = tk.Tk()
    root.title("DNS Speed Test Results")
    root.geometry("800x600")
    root.resizable(True, True)

    tree = ttk.Treeview(root, columns=header, show='headings')
    for col in header:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    for row in rows:
        tree.insert('', tk.END, values=row)

    tree.pack(expand=True, fill=tk.BOTH)

    # Adjust column widths to fit content
    for col in header:
        max_width = max(tkfont.Font().measure(str(item)) for item in [col] + [row[header.index(col)] for row in rows])
        tree.column(col, width=max_width)

    # Add OK button
    ok_button = tk.Button(root, text="OK", command=root.quit)
    ok_button.pack(pady=10)

    root.mainloop()

# Main function
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    use_custom_files = messagebox.askyesno("Custom Files", "Do you want to use custom dnsserver.txt and domains.txt files?")

    if use_custom_files:
        dns_file_path = filedialog.askopenfilename(title="Select DNS Server File", filetypes=[("Text Files", "*.txt")])
        domains_file_path = filedialog.askopenfilename(title="Select Domains File", filetypes=[("Text Files", "*.txt")])

        if dns_file_path and domains_file_path:
            dns_servers = read_from_file(dns_file_path)
            domains = read_from_file(domains_file_path)
        else:
            messagebox.showerror("Error", "Both files must be selected.")
            return
    else:
        dns_servers = get_user_input(default_dns_servers, "DNS Servers")
        domains = get_user_input(default_domains, "Domains")

    # Ensure the format is correct and handle missing names/aliases
    dns_servers = [line.split(' - ') for line in dns_servers]
    domains = [line.split(' - ') for line in domains]

    dns_servers = [(s[0], s[1] if len(s) > 1 else f"custom{index+1}") for index, s in enumerate(dns_servers)]
    domains = [(d[0], d[1] if len(d) > 1 else f"custom{index+1}") for index, d in enumerate(domains)]

    # Extract IP addresses and names
    domain_addresses = [domain[0] for domain in domains]
    domain_aliases = [domain[1] for domain in domains]
    dns_ips = [server[0] for server in dns_servers]
    dns_names = [server[1] for server in dns_servers]

    # Initialize table header
    header = ["DNS Server"] + domain_aliases + ["Average"]

    # Dictionary to store latencies
    latencies = {name: [] for name in dns_names}

    # List to store rows
    rows = []

    # Create a window to display real-time results
    result_window = tk.Tk()
    result_window.title("DNS Speed Test Results")
    result_window.geometry("800x600")
    result_window.resizable(True, True)

    tree = ttk.Treeview(result_window, columns=header, show='headings')
    for col in header:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    tree.pack(expand=True, fill=tk.BOTH)

    result_window.update()

    # Query each DNS server for each domain with progress bar
    for ip, name in tqdm(zip(dns_ips, dns_names), total=len(dns_ips), desc="Testing DNS servers"):
        tqdm.write(f"Testing {name}")
        row = [name]
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [ip]
        for domain in domain_addresses:
            start_time = time.perf_counter()
            try:
                resolver.resolve(domain)
                latency = round((time.perf_counter() - start_time) * 1000, 3)  # Convert to milliseconds and round to 3 decimal places
                row.append(latency)
                latencies[name].append(latency)
            except Exception as e:
                row.append(None)
                latencies[name].append(None)
        
        # Calculate average latency
        valid_times = [t for t in latencies[name] if t is not None]
        if valid_times:
            avg_latency = round(sum(valid_times) / len(valid_times), 3)
            row.append(avg_latency)
        else:
            row.append(None)
        
        rows.append(row)
        tree.insert('', tk.END, values=row)
        result_window.update()

    # Sort rows by average latency
    rows.sort(key=lambda x: (x[-1] is None, x[-1]))

    # Save results to Excel file
    save_to_excel(header, rows)

    # Notify user of completion
    end_program = messagebox.showinfo("Completion", "DNS speed test completed and results saved to speedtest.xlsx")
    if end_program:
        display_results(header, rows)
    else:
        quit()
    

if __name__ == "__main__":
    main()
