list = []
import subprocess
cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description,Path'
proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
for line in proc.stdout:
    if not line.decode()[0].isspace():
        list.append(line.decode().rstrip())


list = list[2:]
paths = []
import re
for path in list:
    match = re.search(r"C:\\.*\.exe", path)
    if match:
        print('Not matched')
        matched_path = match.group()
        paths.append(matched_path)

print(paths)