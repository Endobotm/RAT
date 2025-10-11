# Code from stackoverflow https://stackoverflow.com/questions/44400560/using-windows-gps-location-service-in-a-python-script

import subprocess as sp
import platform, socket, re, uuid, json, psutil, logging

accuracy = 3
pshellcomm = ["powershell"]
pshellcomm.append(
    "add-type -assemblyname system.device; "
    "$loc = new-object system.device.location.geocoordinatewatcher;"
    "$loc.start(); "
    'while(($loc.status -ne "Ready") -and ($loc.permission -ne "Denied")) '
    "{start-sleep -milliseconds 100}; "
    "$acc = %d; "
    "while($loc.position.location.horizontalaccuracy -gt $acc) "
    "{start-sleep -milliseconds 100; $acc = [math]::Round($acc*1.5)}; "
    "$loc.position.location.latitude; "
    "$loc.position.location.longitude; "
    "$loc.position.location.horizontalaccuracy; "
    "$loc.stop()" % (accuracy)
)


p = sp.Popen(pshellcomm, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
(out, err) = p.communicate()
out = re.split("\n", out)

lat = float(out[0])
long = float(out[1])
radius = int(out[2])

locationInfo = f"Latitude: {lat}\nLongitude: {long}\nRadius: {radius}"


# In his own words: Shamelessly combined from google and other stackoverflow like sites to form a single function | https://stackoverflow.com/questions/3103178/how-to-get-the-system-info-with-python | I modified the code a "lil"
def getSystemInfo():
    try:
        info = f"Platform: {platform.system()}\nPlatform Release: {platform.release()}\nPlatform Version: {platform.version()}\nArchitecture: {platform.machine()}\nHostname: {socket.gethostname()}\nIP-Address: {socket.gethostbyname(socket.gethostname())}\nMAC Address: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}\nProcessor: {platform.processor()}\nRAM: {str(round(psutil.virtual_memory().total / (1024.0**3))) + ' GB'}"
        return info
    except Exception as e:
        logging.exception(e)


systemInfo = getSystemInfo()
# You might be sensing a pattern...Yes most of these are from stackoverflow, I wasn't kidding when I said I am your local dumbass, stackoverflow was carrying my ass throughout most of the functions.
# what else dawg, internet? scan for open ports?
print(f"{locationInfo}\n---\n{systemInfo}")
