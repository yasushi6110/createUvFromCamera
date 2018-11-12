# -*- coding: utf-8 -*-
import os
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtUiTools
from maya import OpenMayaUI as omui
import maya.OpenMaya as OpenMaya
from shiboken2 import wrapInstance
import core


class CreateUvFromCamera(QtWidgets.QMainWindow):
    GUI = os.path.join(os.path.dirname(__file__), 'gui.ui')

    def __init__(self, parent=None):
        ptr = omui.MQtUtil.mainWindow()
        widget = wrapInstance(long(ptr), QtWidgets.QWidget)
        QtWidgets.QMainWindow.__init__(self, widget)

        self.ui = QtUiTools.QUiLoader().load(self.GUI)
        self.setCentralWidget(self.ui)
        self.ui_connection()

    def ui_connection(self):
        """ UIとコマンドを接続
        """
        self.ui.okbtn.clicked.connect(self.execute)
        self.ui.setCameraBtn.clicked.connect(self.set_camera_name)

    def set_camera_name(self):
        """ カメラの名前をUIに設定
        """
        camera_name = core.get_selection_camera()
        if not camera_name:
            camera_name = ''
        self.ui.cameraNameEdit.setText(camera_name)

    def execute(self):
        """ UVを作成するコマンドを実行
        """
        # horizontalかVerticalのどちらが選ばれているか取得する
        gate_type = self.ui.cameraGateTypeGrp.checkedButton().text()
        horizontal_flag = False
        if gate_type == 'Horizontal':
            horizontal_flag = True

        # 登録されているものがカメラではなければエラー
        camera_name = self.ui.cameraNameEdit.text()
        if not core.type_camera(camera_name):
            OpenMaya.MGlobal.displayError('Registered names is not Camera !')
            return

        core.create_uv_from_camera(camera_name, horizontal=horizontal_flag)
