import os
import threading
from subprocess import Popen

from PyQt5 import QtCore, QtGui, QtWidgets

import definitions
from .window_progress import ProgressWindow
from .window_driver import DriverConfigViewerWindow
from ui.main import Ui_MainWindow
from utils import commands
from utils.qwidget import is_widget_enabled
from utils.hw_info_worker import HwInfoWorker
from widgets.driver_checkbox import DriverOptionCheckBox
from install.configuration import Driver, DriverConfig
from install.execute_status import ExecuteStatus
from install.task_manager import TaskManager
from install.task import ExecutableTask


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):

    qsig_msg = QtCore.pyqtSignal(str)
    qsig_hwinfo = QtCore.pyqtSignal(object, str)

    def __init__(self, driconfig: DriverConfig):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(
            os.path.join(definitions.DIR_PIC, "icon.ico")))

        self.driconfg = driconfig
        self.progr_window = ProgressWindow()
        self.dri_conf_window = DriverConfigViewerWindow(driconfig)
        self.hwinfo_worker = HwInfoWorker(self.qsig_msg,
                                          self.qsig_hwinfo,
                                          parent=self)
        self.refresh_hwinfo()
        # ---------- driver options ----------
        for option in self.driconfg.get_type("network"):
            self.lan_driver_dropdown.addItem(option.name, option.id)
        # check autoable
        self.lan_driver_dropdown.currentIndexChanged.connect(
            self._dri_on_select)

        for option in self.driconfg.get_type("display"):
            self.display_dri_dropdown.addItem(option.name, option.id)
        # check autoable
        self.display_dri_dropdown.currentIndexChanged.connect(
            self._dri_on_select)

        for option in self.driconfg.get_type("miscellaneous"):
            cb = DriverOptionCheckBox(option.name)
            cb.dri_id = option.id
            self.misc_dri_vbox.addWidget(cb)
            # check autoable
            cb.clicked.connect(self._dri_on_select)
        # ---------- events ----------
        self.hwInfo_refresh_btn.clicked.connect(self.refresh_hwinfo)
        self.disk_mgt_btn.clicked.connect(
            lambda: Popen(["start", "diskmgmt.msc"], shell=True))
        self.install_btn.clicked.connect(self._install)
        self.edit_driver_action.triggered.connect(self.dri_conf_window.show)
        self.at_install_cb.clicked.connect(
            lambda val: self.set_at_options(val))
        self.dri_opt_reset_btn.clicked.connect(self.reset_selection)
        self.set_passwd_cb.clicked.connect(
            lambda: self.set_passwd_txt.setEnabled(
                self.set_passwd_cb.isChecked())
        )
        # ---------- signals ----------
        self.qsig_msg.connect(self.send_msg)
        self.qsig_hwinfo.connect(
            lambda create, text: self.hwinfo_vbox.addWidget(create(text)))

    def send_msg(self, text: str):
        """Display a message to the UI (message box)

        Args:
            text (str): message to be displayed
        """
        self.prog_msg_box.addItem(f"> {text}")
        self.prog_msg_box.verticalScrollBar().setValue(
            self.prog_msg_box.verticalScrollBar().minimum())  # scroll to bottom

    def refresh_hwinfo(self):
        """Rescan and update the hardware information of the computer"""
        for i in reversed(range(self.hwinfo_vbox.count())):
            self.hwinfo_vbox.itemAt(i).widget().setParent(None)
        self.hwinfo_worker.start()

    def set_at_options(self, enable: bool):
        """Enable/disable the auto-installation option checkboxes"""
        for option in self.install_mode_options.children():
            if (option.objectName() != self.at_install_cb.objectName()
                    and isinstance(option, (QtWidgets.QCheckBox, QtWidgets.QRadioButton))):
                option.setEnabled(enable)

        if self._is_autoable():
            self.set_halt_options(enable)

    def set_halt_options(self, enable: bool):
        """Enable/disable the halt option checkboxes"""
        if not self.at_install_cb.isChecked():
            enable = False

        self.at_halt_rb.setEnabled(enable)
        self.at_reboot_rb.setEnabled(enable)
        self.at_nothing_rb.setEnabled(enable)

    def reset_selection(self):
        self.lan_driver_dropdown.setCurrentIndex(0)
        self.display_dri_dropdown.setCurrentIndex(0)
        for widget in self._misc_dri_options():
            widget.setChecked(False)

        self.set_passwd_cb.setChecked(False)

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

    def _install(self):
        """Start the install process"""
        manager = TaskManager(self.qsig_msg, self.progr_window.qsig_progress)
        manager.qsig_install_result.connect(self._post_install)

        # set password
        if self.set_passwd_cb.isChecked():
            manager.add_task(
                commands.set_password(commands.get_current_usrname(), self.set_passwd_txt.toPlainText()))
            self.send_msg(
                f"{commands.get_current_usrname()} 的密碼將會更改為 \"'{self.set_passwd_txt.toPlainText()}\"")

        def prog_close():
            """Terminate the remaining tasks when progress window is closed"""
            if not manager.is_finished():
                manager.abort_tasks()
                self.send_msg("已終止安裝")
        self.progr_window.qsig_close.connect(prog_close)

        self.progr_window.clear_progresses()
        for dri_conf in self.selected_drivers():
            _task = ExecutableTask(
                dri_conf.name, dri_conf.exec_config, dri_conf.path, dri_conf.flags)
            self.progr_window.append_progress(_task, "等待安裝中")
            manager.add_task(_task)

        # start install
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
                    is_widget_enabled(
                        self.at_retry_cb) and self.at_retry_cb.isChecked(),
                    self.async_install_cb.isChecked(),
                ],
                daemon=True).start()
            self.progr_window.exec_()
        else:
            manager.manual_install()

    def _post_install(self, status: ExecuteStatus):
        """Follow-up routine for the installation process

        Args:
            success (bool): whether the all drivers were installed successfully
        """
        if (status != ExecuteStatus.SUCCESS
            and not (status != ExecuteStatus.ABORTED
                     and not self.at_retry_cb.isChecked())):
            pass
        elif (is_widget_enabled(self.at_halt_rb)
              and self.at_halt_rb.isChecked()):
            threading.Timer(
                5,
                lambda: commands.shutdown().execute()
            ).start()
            QtWidgets.QMessageBox.information(self, "完成", "完成，即將自動關機")
        elif (is_widget_enabled(self.at_reboot_rb)
              and self.at_reboot_rb.isChecked()):
            threading.Timer(
                5,
                lambda: commands.reboot().execute()
            ).start()
            QtWidgets.QMessageBox.information(self, "完成", "完成，即將自動重新開機")
        elif (is_widget_enabled(self.at_bios_rb) and self.at_bios_rb.isChecked()):
            threading.Timer(
                5,
                lambda: commands.reboot_uefi().execute()
            ).start()
            QtWidgets.QMessageBox.information(self, "完成", "完成，即將自動重啟至 BIOS")
        else:
            box = QtWidgets.QMessageBox()
            # box.setWindowTitle("完成")
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
        self.set_halt_options(self._is_autoable())
        if not self._is_autoable():
            self.at_nothing_rb.setChecked(True)

    def _is_autoable(self) -> bool:
        return all((dri.exec_config.silentable for dri in self.selected_drivers()))

    def _misc_dri_options(self) -> list[QtWidgets.QCheckBox]:
        """Returns all the "miscellaneous" driver options"""
        return [self.misc_dri_vbox.itemAt(i).widget()
                for i in range(self.misc_dri_vbox.count())]

    # override
    def closeEvent(self, event):
        QtWidgets.QApplication.closeAllWindows()  # force close all windows
        super().closeEvent(event)