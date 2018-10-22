import json
import requests
import subprocess

versions = [ "9.3.4", "9.3.3", "9.3.2", "9.3", "9.2.1", "9.2", "9.1", "9.0.2" ]
#versions = [ "9.3.2" ]

def get_firmwares(iphone):
    firmwares_list = []
    url = 'https://api.ipsw.me/v4/device/' + iphone
    response = requests.get(url)
    #print response.json()
    firmwares = response.json()["firmwares"]
    for firmware in firmwares:
        if firmware["version"] in versions:
            firmwares_list += [[ firmware["version"], firmware["buildid"] ]]
    return firmwares_list

def get_keys(iphone, firmware):
    url = 'https://api.ipsw.me/v4/keys/ipsw/' + iphone + '/' + firmware
    response = requests.get(url)
    #print response.json()
    keys = response.json()["keys"]
    for key in keys:
        if key["filename"].startswith("kernelcache.release"):
            return key["iv"], key["key"], key["filename"]

def download(iphone, firmware):
    url = 'https://api.ipsw.me/v4/ipsw/download/' + iphone + '/' + firmware
    subprocess.call(["rm", "-f", "out.zip"])
    print "Downloading " + url
    subprocess.call(["curl", "-L", url, "-o", "out.zip"])
    print "Downloaded " + url

def get_offset(iphone, firmware):
    iv, key, filename = get_keys(iphone, firmware)
    download(iphone, firmware)
    subprocess.call(["rm", "-f", filename])
    subprocess.call(["unzip", "out.zip", filename])
    subprocess.call(["rm", "-rf", "kcache"])
    subprocess.call(["kcache", "--in", filename, "--iv", iv, "--key", key])
    process = subprocess.Popen(['r2', '-q', 'kcache/kernelcache.bin', '-c', 'is'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    subprocess.call(["rm", "-f", filename])
    for line in out.splitlines():
        if "_memcmp" in line:
            return line

def add_offsets(iphone):
    firmwares = get_firmwares(iphone)
    for firmware in firmwares:
        print "Doing " + iphone + " firmware " + firmware[1] + " version " + firmware[0]
        line = get_offset(iphone, firmware[1])
        print line
        offset = line.split(" ")[1]
        #offset = offset[4:]
        version = firmware[0].replace(".", "")
        if len(version) == 2:
            version += "0"
        casestring = iphone.replace(",", "") + "_" + version
        offsetstring = "case " + casestring
        offsetstring += ": return " + offset + ";\n"
        f=open("offsets.txt", "a+")
        f.write(offsetstring)
        f.close()

if __name__ == "__main__":
    #iphone = "iPhone5,3"
    #iphone = "iPod5,1"
    #add_offsets(iphone)
    iphones = [ "iPhone4,1" ]
    iphones += [ "iPhone5,1", "iPhone5,2", "iPhone5,3", "iPhone5,4" ]
    iphones += [ "iPad2,1", "iPad2,2", "iPad2,3", "iPad2,4" ]
    iphones += [ "iPad3,1", "iPad3,2", "iPad3,3", "iPad3,4", "iPad3,5", "iPad3,6" ]
    iphones += [ "iPod5,1" ]

    for iphone in iphones:
        add_offsets(iphone)


