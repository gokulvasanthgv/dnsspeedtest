# DNS Speedtest

A python script to plot dns latency to csv file


## Windows Executable

For Windows there is also an Executable in the Releases Tab 

https://github.com/gokulvasanthgv/dnsspeedtest/releases/download/Release/dnsspeedtest.zip

Download this zip file and extract. There will be an executable file. Double click dnsspeedtest.exe to run it.

You can modify the dnsserver.txt and domains.txt like you need (instructions given below)

## Usage

This is similar for Windows and Linux.

Open a terminal in the folder you want then type
```
git clone https://github.com/gokulvasanthgv/dnsspeedtest.git
```
Make sure you have python installed.

These modules are used - tqdm, openpyxl, tkinter, dnspython

```
cd dnsspeedtest
pip install -r requirements.txt
```
To start the program, 
```
python dnsspeedtest.py
```
If you want to add a DNS server Open the "dnsserver.txt" file and add an entry in the format "1.1.1.1 - Cloudflare" (i.e. x.x.x.x(space)-(space)name)

If you want to add a Domain Open the "domains.txt" file and add an entry in the format "google.com - Google" (i.e. example.com(space)-(space)domainname)

If run for the first time it creates a new csv file, in the subsequent runs it appends the csv file without creating a ne one everytime.

P.S. I'm not a programmer. I don't even know coding. This was created using the help of AI.
