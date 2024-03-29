from subprocess import check_output
from typing import Optional

import wmi

try:
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from install.models import ExecuteConfig
    from install.task import ExecutableTask, Task
except ImportError:
    from ..install.models import ExecuteConfig
    from ..install.task import ExecutableTask, Task


_WMI = wmi.WMI()


def shutdown(timeout: int | float = 1):
    return ExecutableTask(
        "Shutdown", ExecuteConfig(True, False, fail_time=-1), "shutdown", ("/s", "/t", str(timeout)))


def reboot(timeout: int | float = 1):
    return ExecutableTask(
        "Reboot", ExecuteConfig(True, False, fail_time=-1), "shutdown", ("/r", "/t", str(timeout)))


def reboot_uefi(timeout: int | float = 1):
    return ExecutableTask(
        "Reboot to BIOS", ExecuteConfig(True, False, fail_time=-1), "shutdown", ("/r", "/fw", "/t", str(timeout)))


def cancel_halt():
    """Cancel scheduled shutdown/reboot
    """
    return ExecutableTask("Cancel Halt", "shutdown", ("/a",))


def set_password(username: str, password: Optional[str]):
    if len(password) > 0:
        return ExecutableTask(
            "Set Password",
            ExecuteConfig(True, False, [], 1),
            "powershell",
            options=("Set-LocalUser", "-Name", username, "-Password",
                     f"(ConverTo-SecureString {str(password)} -AsPlainText -Force"))
    else:
        return ExecutableTask(
            "Set Password",
            ExecuteConfig(True, False, [], 1),
            "powershell",
            options=("Set-LocalUser", "-Name", username,
                     "-Password", "(new-object System.Security.SecureString)"))


def get_current_usrname() -> str:
    return check_output(["powershell", "$Env:UserName"]).strip().decode()


def get_users_info() -> list[wmi._wmi_object]:
    return _WMI.Win32_UserAccount()


def initialise_all_disks():
    return ExecutableTask(
        "Disks Initialisation",
        ExecuteConfig(True, False, [], 1),
        "powershell",
        options=("Get-Disk | Where-Object PartitionStyle -Eq \"RAW\" | Initialize-Disk -PassThru | New-Partition -AssignDriveLetter -UseMaximumSize | Format-Volume",))
