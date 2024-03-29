import os
import subprocess
import json


def save_state(name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open("data.json", "r") as f:
        data = json.load(f)
        script = current_dir + "/script.ps1"
        subprocess.call([data["path"], script])
    with open("output.txt", "r") as f:
        paths = []
        for process in f:
            paths.append(process.strip().split(" - ")[-1])

    with open("data.json", "w") as f:
        if name:
            data[name] = paths
        else:
            data["default_state"] = paths
        json.dump(data, f)


def restore_state(name):
    with open("data.json", "r") as f:
        data = json.load(f)
        if not name:
            for app in data["default_state"]:
                subprocess.Popen(app)
        else:
            for app in data[name]:
                subprocess.Popen(app)


def user_onboard():
    with open("data.json", "r") as f:
        data = json.load(f)
        if "path" in data.keys():
            return
        data["path"] = input("Enter the absolute path of powershell.exe: ")

    with open("data.json", "w") as f:
        json.dump(data, f)


def run_app():
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
    run_app()
