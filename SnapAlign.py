#Create By InChil Beak (bigbic127@gmail.com)
import ctypes
import math
from ctypes import windll
from PySide2 import QtCore, QtWidgets,QtGui
from PySide2.QtGui import QVector3D, QQuaternion, QMatrix4x4
from shiboken2 import wrapInstance
from vrAEBase import vrAEBase

def vredMainWindow() : 
    main_window_ptr = getMainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)

class ObjectSnapping(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
        self.addLoop()
        self.user32 = ctypes.windll.user32
        #init
        self.isActive = False
        self.isGrid = True
        self.isPressed = False
        self.isReleased = False
        self.isMoveKey = False
        self.isRotKey = False
        self.isScaleKey = False
        self.snapStep = 100.0
        self.rotStep = 1.0
        self.scaleStep = 1.0
        #gridSnap
        self.gridTargetObj = None
        self.gridTargetOriginPos = None
        self.gridTargetOriginRot = None
        self.gridTargetOriginScale = None
        self.refObj = None
        #faceSnap

    def recEvent(self, state):
        vrAEBase.recEvent(self, state)
        
    def loop(self):
        if self.isActive:
            if self.isGrid:
                if self.user32.GetKeyState(0x10)>1 and self.user32.GetKeyState(0x57)>1:
                    self.onKeyPushUp(0)
                elif self.user32.GetKeyState(0x10)>1 and self.user32.GetKeyState(0x45)>1:
                    self.onKeyPushUp(1)
                elif self.user32.GetKeyState(0x10)>1 and self.user32.GetKeyState(0x52)>1:
                    self.onKeyPushUp(2)
                if self.user32.GetKeyState(0x10)>1 and self.user32.GetKeyState(0x01)>1:
                    if getSelectedNode().isValid():
                        if not self.isPressed:
                            self.onGridPressed()
                        if self.refObj and self.gridTargetObj.isValid():
                            if self.isMoveKey:
                                x,y,z = self.refObj.getWorldTranslation()
                                nx = (x-(x%self.snapStep))
                                ny = (y-(y%self.snapStep))
                                nz = (z-(z%self.snapStep))
                                self.gridTargetObj.setWorldTranslation(nx,ny,nz)
                            elif self.isRotKey:
                                #mat = self.refObj.getWorldTransform()
                                #quat = Utils.ListToQuat(mat)
                                #x,y,z = self.refObj.getWorldRotation()
                                #self.gridTargetObj.setRotation(x,y,z)
                                pass
                            elif self.isScaleKey:
                                pass #Scale
                else:
                    if self.isReleased:
                        self.onGridReleased()
            else:
                pass #Face Snap
                
    def setActive(self,state):
        self.isActive = state
        if state:
            self.isMoveKey = True
        else:
            self.isMoveKey = False
        self.isRotKey = False
        self.isScaleKey = False

    def setGrid(self,state):
        self.isGrid = state
    
    def setStep(self,value):
        self.snapStep = value
        self.scaleStep = value * 0.01

    def onKeyPushUp(self,v):
        if v == 0:
            self.isMoveKey = True
            self.isRotKey = False
            self.isScaleKey = False
        elif v == 1:
            self.isMoveKey = False
            self.isRotKey = True
            self.isScaleKey = False
        else:
            self.isMoveKey = False
            self.isRotKey = False
            self.isScaleKey = True


    def onGridPressed(self):
        #vrLogWarning("Pressed")
        self.isPressed = true
        self.isReleased = true
        self.gridTargetObj = getSelectedNode()
        self.gridTargetOriginPos = self.gridTargetObj.getWorldTranslation()
        self.gridTargetOriginRot = self.gridTargetObj.getWorldRotation()
        self.gridTargetOriginScale = self.gridTargetObj.getWorldScale()
        if self.isMoveKey:
            vrUndoService.beginBlockUndo()
            self.refObj = createNode("Transform3D","RefObj",False)
            vrUndoService.endBlockUndo()
            self.refObj.setWorldTranslation(self.gridTargetOriginPos[0],self.gridTargetOriginPos[1],self.gridTargetOriginPos[2])
            self.refObj.setRotation(self.gridTargetOriginRot[0],self.gridTargetOriginRot[1],self.gridTargetOriginRot[2])
            self.refObj.setScale(self.gridTargetOriginScale[0],self.gridTargetOriginScale[1],self.gridTargetOriginScale[2])
            rotPivot = getTransformNodeRotatePivot(self.gridTargetObj,True)
            setTransformNodeRotatePivot(self.refObj,rotPivot.x(),rotPivot.y(),rotPivot.z(),True)
            selectNode(self.refObj)
        elif self.isRotKey:
            pass
        elif self.isScaleKey:
            pass
       
    def onGridReleased(self):
        #vrLogWarning("Released")
        self.isPressed = false
        self.isReleased = false
        if self.isMoveKey:
            selectNode(self.gridTargetObj)
            if self.refObj:
                vrUndoService.beginBlockUndo()
                deleteNode(self.refObj)
                vrUndoService.endBlockUndo()
        elif self.isRotKey:
            pass
        elif self.isScaleKey:
            pass
        self.gridTargetObj = None
        self.gridTargetOriginPos = None
        self.gridTargetOriginRot = None
        self.gridTargetOriginScale = None
        #updateScene()

class Utils():
    @staticmethod
    def Distance(pos1, pos2):
        dis = math.sqrt(pow(pos2.x - pos1.x,2) + pow(pos2.y - pos1.y, 2) + pow(pos2.z - pos1.z, 2))
        return abs(dis)

    @staticmethod
    def RadToDeg(v):
        deg = v/math.pi * 180.0
        return deg

    @staticmethod
    def DegToRad(v):
        rad = v * math.pi / 180.0
        return rad
        
    @staticmethod
    def VectorAngle(vec1,vec2):
        n1 = vec1.normalized()
        n2 = vec2.normalized()
        return  Utils.RadToDeg(math.acos(QVector3D.dotProduct(n1,n2)))

    @staticmethod
    def QuatToMatrix4(v):
        xx = v.x() ** 2
        xy = v.x() * v.y()
        xz = v.x() * v.z()
        xw = v.x() * v.scalar()
        yy = v.y() ** 2
        yz = v.y() * v.z()
        yw = v.y() * v.scalar()
        zz = v.z() ** 2
        zw = v.z() * v.scalar()
        ma = 1 - 2 * (yy + zz)
        mb = 2 * (xy - zw)
        mc = 2 * (xz + yw)
        me = 2 * (xy + zw)
        mf = 1 - 2 * (xx + zz)
        mg = 2 * (yz - xw)
        mi = 2 * (xz - yw)
        mj = 2 * (yz + xw)
        mk = 1 - 2 * (xx + yy)
        return QMatrix4x4(ma,mb,mc,0.0,me,mf,mg,0.0,mi,mj,mk,0.0,0.0,0.0,0.0,1.0)

    @staticmethod
    def ListToQuat(mat):
        trace = mat[0] + mat[5] + mat[10]
        if trace > 1e-08:
            s = math.sqrt(1.0 + trace) * 2
            x = (mat[9] - mat[6]) / s
            y = (mat[2] - mat[8]) / s
            z = (mat[4] - mat[1]) / s
            w = 0.25 * s
        else:
            if mat[0] > mat[5] and mat[0] > mat[10]:
                s = math.sqrt(1.0 + mat[0] - mat[5] - mat[10]) * 2
                x = 0.25 * s
                y = (mat[4] + mat[1]) / s
                z = (mat[2] + mat[8]) / s
                w = (mat[9] - mat[6]) / s
            elif mat[5] > mat[10]:
                s = math.sqrt(1.0 + mat[5] - mat[0] - mat[10]) * 2
                x = (mat[4] + mat[1]) / s
                y = 0.25 * s
                z = (mat[9] + mat[6]) / s
                w = (mat[2] - mat[8]) / s
            else:
                s = math.sqrt(1.0 + mat[10] - mat[0] - mat[5]) * 2
                x = (mat[2] + mat[8]) / s
                y = (mat[9] + mat[6]) / s
                z = 0.25 * s
                w = (mat[4] - mat[1]) / s
        return QQuaternion(w, x, y, z)

class SnapAndAlign(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(SnapAndAlign, self).__init__(parent)
        self.setup_ui()
        self.setDefined()

    def setup_ui(self):
        #self.setWindowTitle("Snap and Align")
        #self.setGeometry(100,30,0,0)
        iconPath = "C:\\Users\\VR\\Documents\\Autodesk\\VRED-13.31\\SnapAlign"
        self.widget = QtWidgets.QWidget(self)
        #Layout
        self.rootVLayout = QtWidgets.QVBoxLayout(self)
        self.rootLayout = QtWidgets.QHBoxLayout(self)
        self.widget.setLayout(self.rootVLayout)
        self.rootVLayout.addLayout(self.rootLayout)
        self.snapGroupBox = QtWidgets.QGroupBox(self)
        self.alignGroupBox = QtWidgets.QGroupBox(self)
        self.snapGroupBox.setTitle("Snap")
        self.alignGroupBox.setTitle("Align")
        self.rootLayout.addWidget(self.snapGroupBox)
        self.rootLayout.addWidget(self.alignGroupBox)
        self.snapLayout = QtWidgets.QHBoxLayout(self)
        self.alignLayout = QtWidgets.QHBoxLayout(self)
        self.snapGroupBox.setLayout(self.snapLayout)
        self.alignGroupBox.setLayout(self.alignLayout)
        self.snapButton = QtWidgets.QPushButton("",self)
        self.snapButton.clicked.connect(self.onSnapButtonClicked)
        self.snapIcon = QtGui.QIcon()
        self.snapIcon.addPixmap(iconPath+"\\Icons\\magnetism.png",QtGui.QIcon.Active,QtGui.QIcon.On)
        self.snapIcon.addPixmap(iconPath+"\\Icons\\magnetismN.png",QtGui.QIcon.Active,QtGui.QIcon.Off)
        self.snapButton.setIcon(self.snapIcon)
        self.snapButton.setIconSize(QtCore.QSize(32,32))
        self.snapButton.setMinimumSize(32,32)
        self.snapLayout.addWidget(self.snapButton)
        self.snapHLayout = QtWidgets.QVBoxLayout(self)
        self.snapLayout.addLayout(self.snapHLayout)
        self.snapGridLayout = QtWidgets.QHBoxLayout(self)
        self.snapFaceLayout = QtWidgets.QHBoxLayout(self)
        self.snapHLayout.addLayout(self.snapGridLayout)
        self.snapHLayout.addLayout(self.snapFaceLayout)
        self.snapGridRadioButton = QtWidgets.QRadioButton("Grid",self)
        self.snapGridSpinBoxW = QtWidgets.QSpinBox(self)
        self.snapGridSpinBoxE = QtWidgets.QSpinBox(self)
        self.snapGridSpinBoxR = QtWidgets.QSpinBox(self)
        self.snapGridLayout.addWidget(self.snapGridRadioButton)
        self.snapGridLayout.addWidget(self.snapGridSpinBoxW)
        self.snapGridLayout.addWidget(self.snapGridSpinBoxE)
        self.snapGridLayout.addWidget(self.snapGridSpinBoxR)
        self.snapFaceRadioButton = QtWidgets.QRadioButton("Face",self)
        self.snapFaceButton = QtWidgets.QPushButton("Select Object",self)
        self.snapFaceLayout.addWidget(self.snapFaceRadioButton)
        self.snapFaceLayout.addWidget(self.snapFaceButton)        
        self.snapButton.setCheckable(True)
        self.snapGridRadioButton.setChecked(True)
        self.snapGridSpinBoxW.setAlignment(QtGui.Qt.AlignRight)
        self.snapGridSpinBoxW.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.snapGridSpinBoxW.setPrefix("W: ")
        self.snapGridSpinBoxW.setMaximum(9999.0)
        self.snapGridSpinBoxW.setValue(100.0)
        self.snapGridSpinBoxW.valueChanged.connect(self.setStepChange)
        self.snapGridSpinBoxE.setAlignment(QtGui.Qt.AlignRight)
        self.snapGridSpinBoxE.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.snapGridSpinBoxE.setPrefix("E: ")
        self.snapGridSpinBoxE.setMaximum(9999.0)
        self.snapGridSpinBoxE.setValue(100.0)
        self.snapGridSpinBoxR.setAlignment(QtGui.Qt.AlignRight)
        self.snapGridSpinBoxR.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.snapGridSpinBoxR.setPrefix("R: ")
        self.snapGridSpinBoxR.setMaximum(9999.0)
        self.snapGridSpinBoxR.setValue(100.0)
        self.snapGridSpinBoxE.setEnabled(False)
        self.snapGridSpinBoxR.setEnabled(False)
        self.snapGridRadioButton.clicked.connect(self.onChange)
        self.snapFaceRadioButton.clicked.connect(self.onChange)
        self.snapFaceRadioButton.setEnabled(False)
        self.snapFaceButton.setEnabled(False)        
        self.setWidget(self.widget)        
        self.alignButton = QtWidgets.QPushButton("",self)
        self.alignButton.clicked.connect(self.onAlignClicked)
        self.alignButton.setIcon(QtGui.QIcon(iconPath+"\\Icons\\align.png"))
        self.alignButton.setIconSize(QtCore.QSize(32,32)) 
        self.alignButton.setMinimumSize(32,32)
        self.alignLayout.addWidget(self.alignButton)
        self.alignHLayout = QtWidgets.QVBoxLayout(self) 
        self.alignLayout.addLayout(self.alignHLayout)
        self.snapAxisLayout = QtWidgets.QHBoxLayout(self)
        self.alignObjLayout = QtWidgets.QHBoxLayout(self)
        self.alignHLayout.addLayout(self.snapAxisLayout)
        self.alignHLayout.addLayout(self.alignObjLayout)
        self.alignXRadioButton = QtWidgets.QRadioButton("X",self)
        self.alignYRadioButton = QtWidgets.QRadioButton("Y",self)
        self.alignZRadioButton = QtWidgets.QRadioButton("Z",self)
        self.snapAxisLayout.addWidget(self.alignXRadioButton)
        self.snapAxisLayout.addWidget(self.alignYRadioButton)
        self.snapAxisLayout.addWidget(self.alignZRadioButton)
        self.alignCheckBox = QtWidgets.QCheckBox("Invert",self)
        self.alignCenterCheckBox = QtWidgets.QCheckBox("Center",self)
        self.alignObjLayout.addWidget(self.alignCheckBox)
        self.alignObjLayout.addWidget(self.alignCenterCheckBox)
        self.alignXRadioButton.setChecked(True)
        self.alignXRadioButton.clicked.connect(self.onAxisChange)
        self.alignYRadioButton.clicked.connect(self.onAxisChange)
        self.alignZRadioButton.clicked.connect(self.onAxisChange)        
        self.verticalSpacer = QtWidgets.QSpacerItem(40000,20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.verticalSpacer2 = QtWidgets.QSpacerItem(20,40000, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.rootLayout.addItem(self.verticalSpacer)
        self.rootVLayout.addItem(self.verticalSpacer2)       
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        #self.setStyleSheet("background-color:rgba(120,120,120,120);border:1px;")
        #self.setStyleSheet("background:transparent")
        self.setMaximumHeight(200)
        vredMainWindow().addDockWidget(QtCore.Qt.TopDockWidgetArea, self)

    def setDefined(self):
        self.snapObj = ObjectSnapping()
        self.alignAxis = 0

    def onSnapButtonClicked(self):
        if self.snapButton.isChecked():
            vrLogWarning("Start Snap")
            self.snapObj.setActive(True)
        else:
            vrLogWarning("Stop Snap")
            self.snapObj.setActive(False)

    def onChange(self):
        if self.snapGridRadioButton.isChecked():
            self.snapObj.setGrid(True)
        else:
            self.snapObj.setGrid(False)

    def setStepChange(self,value):
        #vrLogWarning("Step Change")
        self.snapObj.setStep(self.snapGridSpinBoxW.value())

    def onAxisChange(self):
        if self.alignXRadioButton.isChecked():
            self.alignAxis = 0
        elif self.alignYRadioButton.isChecked():
            self.alignAxis = 1
        else:
            self.alignAxis = 2

    def onAlignClicked(self):
        selobjs = getSelectedNodes()
        if len(selobjs) == 2:
            refPos = selobjs[0].getWorldTranslation()
            bbox = selobjs[0].getBoundingBox()
            bboxCenter = getBoundingBoxCenter(selobjs[0],true)
            sbbox = selobjs[1].getBoundingBox()
            sbboxCenter = getBoundingBoxCenter(selobjs[1],true)
            if self.alignAxis == 0:
                if self.alignCenterCheckBox.isChecked():
                    selobjs[0].setWorldTranslation(sbboxCenter.x(),refPos[1],refPos[2])
                else:
                    if self.alignCheckBox.isChecked():
                        selobjs[0].setWorldTranslation(sbbox[0]-(bbox[3]-bboxCenter.x()),refPos[1],refPos[2])
                    else:
                        selobjs[0].setWorldTranslation(sbbox[3]-(bbox[0]-bboxCenter.x()),refPos[1],refPos[2])            
            elif self.alignAxis == 1:
                if self.alignCenterCheckBox.isChecked():
                    selobjs[0].setWorldTranslation(refPos[0],sbboxCenter.y(),refPos[2])
                else:
                    if self.alignCheckBox.isChecked():
                        selobjs[0].setWorldTranslation(refPos[0],sbbox[4]-(bbox[1]-bboxCenter.y()),refPos[2])
                    else:
                        selobjs[0].setWorldTranslation(refPos[0],sbbox[1]-(bbox[4]-bboxCenter.y()),refPos[2])
            else:
                if self.alignCenterCheckBox.isChecked():
                        selobjs[0].setWorldTranslation(refPos[0],refPos[1],sbboxCenter.z())
                else:
                    if self.alignCheckBox.isChecked():
                        selobjs[0].setWorldTranslation(refPos[0],refPos[1],sbbox[5]-(bbox[2]-bboxCenter.z()))
                    else:
                        selobjs[0].setWorldTranslation(refPos[0],refPos[1],sbbox[2]-(bbox[1]-bboxCenter.z()))
        else:
            vrLogWarning("Select Object")

if __name__ == "__main__":
    vredSnap = SnapAndAlign()
    vredSnap.show()