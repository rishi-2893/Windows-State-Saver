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
$windows | Out-File -FilePath "save-state/output.txt" -Encoding UTF8