import gzip
import urllib.request
import xml.etree.ElementTree as ET

EPG_URL = "https://iptv-epg.org/files/epg-gb.xml.gz"

DOWNLOAD = "guide.xml.gz"
OUTPUT = "epg.xml"

print("Downloading EPG...")
urllib.request.urlretrieve(EPG_URL, DOWNLOAD)

print("Extracting...")
with gzip.open(DOWNLOAD, "rb") as f:
    data = f.read()

root = ET.fromstring(data)

wanted = set()

with open("wanted_channels.txt", encoding="utf-8") as f:
    for line in f:
        name = line.strip()
        if name:
            wanted.add(name)

channel_ids = set()

new_root = ET.Element("tv")

for ch in root.findall("channel"):
    names = [
        d.text.strip()
        for d in ch.findall("display-name")
        if d.text
    ]

    if any(n in wanted for n in names):
        new_root.append(ch)
        channel_ids.add(ch.attrib["id"])

count = 0

for prog in root.findall("programme"):
    if prog.attrib["channel"] in channel_ids:
        new_root.append(prog)
        count += 1

tree = ET.ElementTree(new_root)
tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)

print("Channels:", len(channel_ids))
print("Programmes:", count)
print("Done!")
