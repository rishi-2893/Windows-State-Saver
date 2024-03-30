import os
import subprocess
import json
import importlib_resources

# C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe

# ----------------V1---------------------
# current_dir = os.path.dirname(os.path.abspath(__file__))
# data_json = current_dir + '/data.json'
# output_txt = current_dir + '/output.txt'
# script_ps = current_dir + '/script.ps1'


# ----------------V2---------------------

# Get absolute path of current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

my_resources = importlib_resources.files("app")
data_json = my_resources / "data.json"
output_txt = my_resources / "output.txt"
script_ps = my_resources / "script.ps1"

if not os.path.exists(data_json):
    with open(data_json, "w") as f:
        json.dump({"default_state": []}, f)

script = """
$scriptBlock = {
    Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        using System.Text;
        using System.Diagnostics;
        using System.IO;
        
        public class WindowInfo {
            public delegate void ThreadDelegate(IntPtr hWnd, IntPtr lParam);
            
            [DllImport("user32.dll")]
            public static extern bool EnumThreadWindows(int dwThreadId, 
                ThreadDelegate lpfn, IntPtr lParam);
            
            [DllImport("user32.dll", CharSet=CharSet.Auto, SetLastError=true)]
            public static extern int GetWindowText(IntPtr hwnd, 
                StringBuilder lpString, int cch);
            
            [DllImport("user32.dll", CharSet=CharSet.Auto, SetLastError=true)]
            public static extern Int32 GetWindowTextLength(IntPtr hWnd);

            [DllImport("user32.dll")]
            public static extern bool IsIconic(IntPtr hWnd);

            [DllImport("user32.dll")]
            public static extern bool IsWindowVisible(IntPtr hWnd);

            [DllImport("user32.dll")]
            public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

            public static string GetTitle(IntPtr hWnd) {
                var len = GetWindowTextLength(hWnd);
                StringBuilder title = new StringBuilder(len + 1);
                GetWindowText(hWnd, title, title.Capacity);
                return title.ToString();
            }
            
            public static string GetProcessPath(IntPtr hWnd) {
                uint processId;
                GetWindowThreadProcessId(hWnd, out processId);
                Process process = Process.GetProcessById((int)processId);
                return process.MainModule.FileName;
            }
        }
"@
}

Invoke-Command -ScriptBlock $scriptBlock -NoNewScope

$excludedApps = @("Settings", "Windows Input Experience", "Windows PowerShell")

$windows = New-Object System.Collections.ArrayList
Get-Process | Where-Object { $_.MainWindowTitle } | ForEach-Object {
    $_.Threads.ForEach({
        [void][WindowInfo]::EnumThreadWindows($_.Id, {
            param($hwnd, $lparam)
            if ([WindowInfo]::IsIconic($hwnd) -or [WindowInfo]::IsWindowVisible($hwnd)) {
                $title = [WindowInfo]::GetTitle($hwnd)
                $path = [WindowInfo]::GetProcessPath($hwnd)
                
                # Check if the title does not match any of the excluded apps
                if (-not ($excludedApps -contains $title)) {
                    $windows.Add("$title - $path")
                }
            }
        }, 0)
    })
}
""" + f'$windows | Out-File -FilePath "{current_dir}/output.txt" -Encoding UTF8'

if not os.path.exists(script_ps):
    with open(script_ps, "w") as f:
        f.write(script)

def save_state(name):
    with open(data_json, "r") as f:
        data = json.load(f)
        subprocess.call([data["path"], script_ps])
    with open(output_txt, "r") as f:
        paths = []
        for process in f:
            paths.append(process.strip().split(" - ")[-1])

    with open(data_json, "w") as f:
        if name:
            data[name] = paths
        else:
            data["default_state"] = paths
        json.dump(data, f)


def restore_state(name):
    with open(data_json, "r") as f:
        data = json.load(f)
        if not name:
            for app in data["default_state"]:
                subprocess.Popen(app)
        else:
            for app in data[name]:
                subprocess.Popen(app)


def user_onboard():
    with open(data_json, "r") as f:
        data = json.load(f)
        if "path" in data.keys():
            return
        data["path"] = input("Enter the absolute path of powershell.exe: ")

    with open(data_json, "w") as f:
        json.dump(data, f)


def run():
    """
    Start the app
    """
    user_onboard()
    app_status = True
    while app_status:
        resp = input(
            "Welcome to the save state app\nPress 'q' to quit\nPress 's' to save state\nPress 'r' to restore\n"
        )
        if resp == "q":
            app_status = False
        elif resp == "s":
            name = input(
                "Do you want to name this state?\nHit enter if not, else write it!\n"
            )
            save_state(name)
        elif resp == "r":
            name = input(
                "Enter the state name, or hit enter to restore default state\n"
            )
            restore_state(name)


if __name__ == "__main__":
    run()
