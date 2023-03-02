import sys
import os
import threading
from subprocess import Popen

from PyQt5 import QtCore, QtGui, QtWidgets

from hw_info_worker import HwInfoWorker
from ui.main import Ui_MainWindow
from window_progress import ProgressWindow
from window_driver import DriverConfigViewerWindow
from install.configuration import DriverType, DriverConfig
from install.install_manager import InstallManager
from install.task import Task


if getattr(sys, 'frozen', False):
    ROOTDIR = os.path.dirname(sys.executable)
elif __file__:
    ROOTDIR = os.path.dirname(os.path.dirname(__file__))


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    
    qsig_msg = QtCore.pyqtSignal(str)
    qsig_hwinfo = QtCore.pyqtSignal(object, str)
    
    def __init__(self, driconfig: DriverConfig):
        super().__init__()
        self.setupUi(self)

        self.driconfg = driconfig
        self.progr_window = ProgressWindow()
        self.dri_conf_window = DriverConfigViewerWindow(driconfig)
        self.hwinfo_worker = HwInfoWorker(self.qsig_msg,
                                          self.qsig_hwinfo,
                                          parent=self)
        self.refresh_hwinfo()
        # ----- driver options -----
        for option in self.driconfg.get_type("network"):
            self.lan_driver_dropdown.addItem(option.name, option.id)
        
        for option in self.driconfg.get_type("display"):
            self.display_dri_dropdown.addItem(option.name, option.id)
        
        for option in self.driconfg.get_type("miscellaneous"):
            cb = QtWidgets.QCheckBox(option.name)
            # NOTE: QCheckBox cannot be assigned a value to the UI element like QComboBox 
            setattr(cb, "dri_id", option.id)  # use setattr() to achive the same functionality
            self.misc_dri_vbox.addWidget(cb)
        # ---------- events ----------
        self.hwInfo_refresh_btn.clicked.connect(self.refresh_hwinfo)
        self.disk_mgt_btn.clicked.connect(lambda: Popen(["start", "diskmgmt.msc"], shell=True))
        self.install_btn.clicked.connect(self.install)
        self.edit_driver_action.triggered.connect(self.dri_conf_window.show)
        # ---------- signals ----------
        self.qsig_msg.connect(self.send_msg)
        self.qsig_hwinfo.connect(
            lambda create, text: self.hwinfo_vbox.addWidget(create(text)))
    
    def send_msg(self, text: str): 
        self.prog_msg_box.addItem(f"> {text}")
        self.prog_msg_box.verticalScrollBar().setValue(
            self.prog_msg_box.verticalScrollBar().maximum())  # scroll to bottom
    
    def refresh_hwinfo(self):
        for i in reversed(range(self.hwinfo_vbox.count())):
            self.hwinfo_vbox.itemAt(i).widget().setParent(None)
        self.hwinfo_worker.start()
    
    def install(self):
        manager = InstallManager(self.qsig_msg, self.progr_window.qsig_progress)
        manager.qsig_successful.connect(self.post_install)
        
        # terminate the remaining tasks when progress window is closed
        def prog_close():
            nonlocal self, manager
            if not manager.is_finished():
                manager.abort()
                self.send_msg("已終止安裝")
        self.progr_window.qsig_close.connect(prog_close)
        
        self.progr_window.clear_progress()
        # lan driver
        if self.lan_driver_dropdown.currentData() is not None:
            _conf = self.driconfg.get(self.lan_driver_dropdown.currentData())
            
            self.progr_window.append_progress(_conf, "等待安裝中")
            manager.add_task(Task(_conf))
        # display driver
        if self.display_dri_dropdown.currentData() is not None:
            _conf = self.driconfg.get(self.display_dri_dropdown.currentData())
            
            self.progr_window.append_progress(_conf, "等待安裝中")
            manager.add_task(Task(_conf))
        # other driver
        for i in range(self.misc_dri_vbox.count()):
            cb = self.misc_dri_vbox.itemAt(i).widget()
            if not cb.isChecked():
                continue
            _conf = self.driconfg.get(cb.dri_id)
            self.progr_window.append_progress(_conf, "等待安裝中")
            manager.add_task(Task(_conf))
        
        # debug
        from install.configuration import Driver, DriverType
        __dri1 = Driver("ididid", DriverType.DISPLAY, "test1", "",
                       os.path.dirname(os.path.dirname(__file__)) + '\\driver\\print.exe',
                       False, [])
        __dri2 = Driver("ididid2", DriverType.DISPLAY, "test2", "",
                       os.path.dirname(os.path.dirname(__file__)) + '\\driver\\print.exe',
                       False, [])
        __dri3 = Driver("ididid3", DriverType.DISPLAY, "test3", "",
                       os.path.dirname(os.path.dirname(__file__)) + '\\driver\\print.exe',
                       False, [])

        manager.add_task(Task(__dri1))
        manager.add_task(Task(__dri2))
        manager.add_task(Task(__dri3))
        self.progr_window.append_progress(__dri1, "等待安裝中")
        self.progr_window.append_progress(__dri2, "等待安裝中")
        self.progr_window.append_progress(__dri3, "等待安裝中")
        
        # start install
        if self.at_install_cb.isChecked():
            t = threading.Thread(
                target=manager.auto_install, args=[self.async_install_cb.isChecked()], daemon=True)
            t.start()
            self.progr_window.exec_()
        else:
            manager.manual_install()
    
    def post_install(self, success: bool):
        if not success:
            pass
        elif self.at_halt_rb.isChecked():
            t = threading.Timer(5, lambda: Popen(["shutdown", "/s", "/t", "1"]))
            t.start()
            QtWidgets.QMessageBox.information(self, '完成', '安裝成功，即將自動關機')
        else:
            box = QtWidgets.QMessageBox()
            box.setIcon(QtWidgets.QMessageBox.Information)
            box.setWindowTitle('完成')
            box.setText('搞掂')
            box.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close)
            btnok = box.button(QtWidgets.QMessageBox.Ok)
            btnok.setText('好')
            btnclose = box.button(QtWidgets.QMessageBox.Close)
            btnclose.setText('關閉程式')
            box.exec_()
            
            if box.clickedButton() == btnclose:
                exit(0)

    def closeEvent(self, event):
        # print(QtWidgets.QApplication.topLevelWidgets())
        QtWidgets.QApplication.closeAllWindows()  # force close all windows
        super().closeEvent(event)
    
    