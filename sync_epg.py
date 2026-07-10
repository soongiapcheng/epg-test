#!/usr/bin/env python3

import gzip
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

# ------------------------------------------------------------------
# EPG URL
# ------------------------------------------------------------------
EPG_URL = "https://iptv-epg.org/files/epg-gb.xml.gz"

DOWNLOAD = "guide.xml.gz"
OUTPUT = "epg.xml"
WANTED = "wanted_channels.txt"

print("=" * 60)
print("Simple GitHub EPG Test")
print("=" * 60)

print(f"Current directory : {os.getcwd()}")
print(f"Python version    : {sys.version}")
print()

# -------------------------------------------------------------
# Download
# -------------------------------------------------------------
print(f"Downloading:\n{EPG_URL}")

try:
    urllib.request.urlretrieve(EPG_URL, DOWNLOAD)
except Exception as e:
    print("\nERROR downloading file:")
    print(e)
    sys.exit(1)

print("Download completed.")

if not os.path.exists(DOWNLOAD):
    print("Downloaded file not found!")
    sys.exit(1)

print(f"Downloaded size: {os.path.getsize(DOWNLOAD):,} bytes")
print()

# -------------------------------------------------------------
# Read wanted channels
# -------------------------------------------------------------
wanted = []

if os.path.exists(WANTED):
    with open(WANTED, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                wanted.append(line)

print("Wanted keywords:")
for w in wanted:
    print("  -", w)
print()

# -------------------------------------------------------------
# Extract XML
# -------------------------------------------------------------
print("Extracting XML...")

try:
    with gzip.open(DOWNLOAD, "rb") as f:
        xml_data = f.read()
except Exception as e:
    print("Cannot extract gzip:")
    print(e)
    sys.exit(1)

print(f"Extracted XML size: {len(xml_data):,} bytes")
print()

# -------------------------------------------------------------
# Parse XML
# -------------------------------------------------------------
print("Parsing XML...")

try:
    root = ET.fromstring(xml_data)
except Exception as e:
    print("XML parse error:")
    print(e)
    sys.exit(1)

print("XML parsed successfully.")
print()

all_channels = root.findall("channel")
all_programmes = root.findall("programme")

print(f"Total channels   : {len(all_channels)}")
print(f"Total programmes : {len(all_programmes)}")
print()

# -------------------------------------------------------------
# Filter channels
# -------------------------------------------------------------
print("Searching for matching channels...")
print()

new_root = ET.Element("tv")
channel_ids = set()

for ch in all_channels:

    names = [
        d.text.strip()
        for d in ch.findall("display-name")
        if d.text
    ]

    matched = False

    if not wanted:
        matched = True

    else:
        for display_name in names:
            for keyword in wanted:
                if keyword.lower() in display_name.lower():
                    matched = True
                    break
            if matched:
                break

    if matched:
        new_root.append(ch)
        channel_ids.add(ch.attrib["id"])

        print(f"Matched: {ch.attrib['id']}")

        for n in names:
            print(f"   {n}")

        print()

print("-" * 60)
print(f"Matched channels : {len(channel_ids)}")
print()

# -------------------------------------------------------------
# Copy programmes
# -------------------------------------------------------------
programme_count = 0

for prog in all_programmes:
    if prog.attrib.get("channel") in channel_ids:
        new_root.append(prog)
        programme_count += 1

print(f"Matched programmes : {programme_count}")
print()

# -------------------------------------------------------------
# Save XML
# -------------------------------------------------------------
print(f"Saving {OUTPUT}")

tree = ET.ElementTree(new_root)
tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)

if os.path.exists(OUTPUT):
    print("Output created successfully.")
    print(f"Output size: {os.path.getsize(OUTPUT):,} bytes")
else:
    print("Output file was NOT created!")

print()
print("=" * 60)
print("Finished")
print("=" * 60)
