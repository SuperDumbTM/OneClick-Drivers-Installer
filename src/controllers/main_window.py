import os
import threading
import time
from subprocess import Popen

from PyQt5 import QtCore, QtGui, QtWidgets

import definitions
from controllers.install_option_edit_window import InstallOptionEditWindow
from install.driver_option import DriverOption
from install.enums import DriverType, ExecuteStatus, HaltOption
from install.models import Driver, InstallOption
from install.task import ExecutableTask
from install.task_manager import TaskManager
from ui.generated.main_window import Ui_MainWindow
from utils import commands
from utils.hw_info_worker import HwInfoWorker
from utils.qwidget import is_widget_enabled
from widgets.driver_checkbox import DriverOptionCheckBox

from .driver_config_window import DriverConfigWindow
from .install_progress_window import InstallProgressWindow


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):

    qsig_msg = QtCore.pyqtSignal(str)
    qsig_hwinfo = QtCore.pyqtSignal(object, str)

    def __init__(self, driconfig: DriverOption, installopt: InstallOption):
        super().__init__()

        self.driconfg = driconfig
        self.installopt = installopt
        self._hwinfo_worker = HwInfoWorker(
            self.qsig_msg, self.qsig_hwinfo, parent=self)

        self.setupUi(self)
        self.refresh_hwinfo()
        self.reset_fields()

        # ---------- events ----------
        self.hwInfo_refresh_btn.clicked.connect(self.refresh_hwinfo)
        self.disk_mgt_btn.clicked.connect(
            lambda: Popen(["start", "diskmgmt.msc"], shell=True))
        self.install_btn.clicked.connect(self._install)
        self.at_install_cb.clicked.connect(self.set_ati_checked)
        self.dri_opt_reset_btn.clicked.connect(self.reset_fields)
        self.set_passwd_cb.clicked.connect(self.set_passwd_checked)

        self.edit_driver_action.triggered.connect(
            lambda: DriverConfigWindow(driconfig).show())
        self.edit_defaults_action.triggered.connect(
            self._show_defaults_edit_window)

        # ---------- signals ----------
        self.qsig_msg.connect(self.send_msg)
        self.qsig_hwinfo.connect(
            lambda create, text: self.hwinfo_vbox.addWidget(create(text)))

    def send_msg(self, text: str):
        """Display a message to the message box

        Args:
            text (str): message to be displayed
        """
        self.prog_msg_box.addItem(f"> {text}")
        self.prog_msg_box.verticalScrollBar().setValue(
            self.prog_msg_box.verticalScrollBar().maximum())  # scroll to bottom

    def refresh_hwinfo(self):
        """Rescan and update the hardware information of the computer
        """
        for i in reversed(range(self.hwinfo_vbox.count())):
            self.hwinfo_vbox.itemAt(i).widget().setParent(None)
        self._hwinfo_worker.start()

    def set_ati_checked(self, checked: bool):
        """Enable/disable the auto-installation option checkboxes
        """
        self.at_install_cb.setChecked(checked)
        for idx in range(self.install_mode_options.count()):
            widget = self.install_mode_options.itemAt(idx).widget()
            if (widget.objectName() != self.at_install_cb.objectName()
                    and isinstance(widget, (QtWidgets.QCheckBox, QtWidgets.QRadioButton))):
                widget.setEnabled(checked)

        if self.is_selected_autoable():
            self.set_halt_options(checked)

    def set_passwd_checked(self, checked: bool):
        self.set_passwd_cb.setChecked(checked)
        self.set_passwd_txt.setEnabled(
            self.set_passwd_cb.isChecked())

    def set_halt_options(self, enable: bool):
        """Enable/disable the halt option checkboxes
        """
        if not self.at_install_cb.isChecked():
            enable = False

        self.halt_option_dropdown.setEnabled(enable)

    def reset_fields(self):
        """Reset all the input fields to default value.
        """
        self.lan_driver_dropdown.setCurrentIndex(0)
        self.display_dri_dropdown.setCurrentIndex(0)
        for widget in self._misc_dri_options():
            widget.setChecked(False)

        self.set_ati_checked(self.installopt.auto_install)
        self.async_install_cb.setChecked(self.installopt.async_install)
        self.at_retry_cb.setChecked(self.installopt.retry_on_fail)
        self.halt_option_dropdown.setCurrentIndex(
            self.halt_option_dropdown.findData(self.installopt.halt_option))
        self.at_init_disks_cb.setChecked(self.installopt.is_init_disks)
        self.set_passwd_checked(self.installopt.is_set_passwd)
        self.set_passwd_txt.setPlainText(self.installopt.passwd)

    def selected_drivers(self) -> list[Driver]:
        drivers = []
        # network driver
        if self.lan_driver_dropdown.currentData() is not None:
            drivers.append(self.driconfg.get(
                self.lan_driver_dropdown.currentData()))
        # display driver
        if self.display_dri_dropdown.currentData() is not None:
            drivers.append(self.driconfg.get(
                self.display_dri_dropdown.currentData()))
        # miscellaneous driver
        for widget in self._misc_dri_options():
            if not widget.isChecked():
                continue
            elif not isinstance(widget, DriverOptionCheckBox):
                continue
            drivers.append(self.driconfg.get(widget.dri_id))
        return drivers

    def is_selected_autoable(self) -> bool:
        """Returns whether all the selected drivers can be installed with \
            slient /unattend mode.
        """
        return all((dri.exec_config.silentable for dri in self.selected_drivers()))

    def _install(self):
        """Start the install process
        """
        prog_window = InstallProgressWindow()
        manager = TaskManager(self.qsig_msg, prog_window.qsig_progress)
        manager.qsig_install_result.connect(self._post_install)

        # set password
        if self.set_passwd_cb.isChecked():
            _task = commands.set_password(
                commands.get_current_usrname(), self.set_passwd_txt.toPlainText())
            self.send_msg(
                f"{commands.get_current_usrname()} 的密碼將會更改為 \"'{self.set_passwd_txt.toPlainText()}\"")
            manager.add_task(_task)
            prog_window.append_progress(_task, "等待執行中")

        # init disks
        if self.at_init_disks_cb.isChecked():
            _task = commands.initialise_all_disks()
            manager.add_task(_task)
            prog_window.append_progress(_task, "等待執行中")

        prog_window.qsig_abort.connect(lambda: threading.Thread(
            target=manager.abort_tasks).start() if not manager.is_finished() else None)

        for dri_conf in self.selected_drivers():
            _task = ExecutableTask(
                dri_conf.name, dri_conf.exec_config, dri_conf.path, dri_conf.flags)
            prog_window.append_progress(_task, "等待安裝中")
            manager.add_task(_task)

        # ---------- start installation ----------
        if len(manager.tasks) == 0:
            box = QtWidgets.QMessageBox()
            box.setWindowTitle("失敗")
            box.setWindowIcon(self.windowIcon())
            box.setIcon(QtWidgets.QMessageBox.Warning)
            box.setText("未有選擇任何軀動")
            box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            btnok = box.button(QtWidgets.QMessageBox.Ok)
            btnok.setText("好")
            box.exec_()
        elif self.at_install_cb.isChecked():
            threading.Thread(
                target=manager.auto_install,
                args=[
                    (is_widget_enabled(self.at_retry_cb)
                     and self.at_retry_cb.isChecked()),
                    self.async_install_cb.isChecked(),
                ],
                daemon=True).start()
            prog_window.exec_()
        else:
            manager.manual_install()

    def _post_install(self, status: ExecuteStatus):
        """Follow-up routine for the installation process

        Args:
            success (ExecuteStatus): Execution status
        """
        if (status != ExecuteStatus.SUCCESS
            and not (status != ExecuteStatus.ABORTED
                     and not self.at_retry_cb.isChecked())):
            pass
        elif (is_widget_enabled(self.halt_option_dropdown)):
            if self.halt_option_dropdown.currentData() == HaltOption.SHUTDOWN:
                commands.shutdown(5).execute()
                QtWidgets.QMessageBox.information(self, "完成", "即將自動關機")
            elif self.halt_option_dropdown.currentData() == HaltOption.REBOOT:
                commands.reboot(5).execute()
                QtWidgets.QMessageBox.information(self, "完成", "即將重新開機")
            elif self.halt_option_dropdown.currentData() == HaltOption.BIOS:
                retry_cnt = 0
                cmd = commands.reboot_uefi(5)
                cmd.execute()

                while retry_cnt < 5:
                    if cmd.rtcode == 0:
                        break
                    cmd.execute()
                    time.sleep(0.3)
                    retry_cnt += 1
                else:
                    QtWidgets.QMessageBox.information(
                        self, "錯誤", "無法重啟至 BIOS")
                    self.send_msg(f"重啟至 BIOS 指令返回代碼：{cmd.rtcode}")
                    return
                QtWidgets.QMessageBox.information(
                    self, "完成", "即將自動重啟至 BIOS")
        else:
            box = QtWidgets.QMessageBox()
            box.setWindowIcon(self.windowIcon())
            box.setIcon(QtWidgets.QMessageBox.Information)
            box.setText("完成")
            box.setStandardButtons(
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close)
            btnok = box.button(QtWidgets.QMessageBox.Ok)
            btnok.setText("好")
            btnclose = box.button(QtWidgets.QMessageBox.Close)
            btnclose.setText("關閉程式")
            box.exec_()

            if box.clickedButton() == btnclose:
                QtWidgets.qApp.exit(0)

    def _dri_on_select(self):
        """Analyse and update execution options for auto installation mode
        based on user selection on to be installed drivers.

        E.g. If selected drivers contains non-autoable drivers,\
            disable execution options for auto installation mode
        """
        self.set_halt_options(self.is_selected_autoable())
        # if not self.is_selected_autoable():
        #     self.at_nothing_rb.setChecked(True)

    def _misc_dri_options(self) -> list[QtWidgets.QCheckBox]:
        """Returns all the "miscellaneous" driver options
        """
        return [self.misc_dri_vbox.itemAt(i).widget()
                for i in range(self.misc_dri_vbox.count())]

    def _show_defaults_edit_window(self):
        window = InstallOptionEditWindow(self.installopt)

        def set_installopt(new):
            self.installopt = new
        window.qsig_save.connect(set_installopt)
        window.exec_()

    # override
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        self.setWindowIcon(
            QtGui.QIcon(os.path.join(definitions.DIR_PIC, "icon.ico")))
        # ---------- driver options ----------
        for option in self.driconfg.get_type(DriverType.NET):
            self.lan_driver_dropdown.addItem(option.name, option.id)
        self.lan_driver_dropdown.currentIndexChanged.connect(
            self._dri_on_select)

        for option in self.driconfg.get_type(DriverType.DISPLAY):
            self.display_dri_dropdown.addItem(option.name, option.id)
        self.display_dri_dropdown.currentIndexChanged.connect(
            self._dri_on_select)

        for option in self.driconfg.get_type(DriverType.MISC):
            cb = DriverOptionCheckBox(option.name)
            cb.dri_id = option.id
            self.misc_dri_vbox.addWidget(cb)
            cb.clicked.connect(self._dri_on_select)
        # ---------- halt options ----------
        for option in HaltOption:
            self.halt_option_dropdown.addItem(option.value, option)

    # override
    def closeEvent(self, event):
        QtWidgets.QApplication.closeAllWindows()  # force close all windows
        super().closeEvent(event)
