from enum import Enum


class DriverType(str, Enum):

    NET = "network"
    DISPLAY = "display"
    MISC = "miscellaneous"


class ExecuteStatus(Enum):
    PENDING = 1
    INPROGRESS = 2
    EARLYEXIT = 3
    SUCCESS = 4
    ERROR = 5
    FAILED = 6
    ABORTING = 7
    ABORTED = 8

    def text(self):
        match self:
            case ExecuteStatus.PENDING:
                return "等待執行中"
            case ExecuteStatus.INPROGRESS:
                return "執行中"
            case ExecuteStatus.EARLYEXIT:
                return "過早結束執行"
            case ExecuteStatus.SUCCESS:
                return "已完成"
            case ExecuteStatus.ERROR:
                return "執行時出現錯誤"
            case ExecuteStatus.FAILED:
                return "失敗"
            case ExecuteStatus.ABORTING:
                return "正在結束執行中"
            case ExecuteStatus.ABORTED:
                return "已取消"
        return ""


class HaltOption(Enum):
    NONE = "沒有動作"
    SHUTDOWN = "關機"
    REBOOT = "重新開機"
    BIOS = "進入 BIOS"
