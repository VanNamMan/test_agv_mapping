
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# from PyQt5.QtChart import *
from PyQt5.QtCore import QT_VERSION_STR
import threading
import os
import time
import json
from functools import partial
# import numpy as np
# import cv2
# import shutil
# import platform
# import psutil
# import GPUtil
import hashlib
# import imutils
# import wmi

def get_all_process_running():
    c = wmi.WMI ()
    return [process for process in c.Win32_Process()]

def terminate(process_name):
    c = wmi.WMI()
    for process in c.Win32_Process():
        if process.Name == process_name:
            process.Terminate()
            print("Terminate process %s"%process_name)
        pass

BB = QDialogButtonBox

class ImageView(QDialog):
    DEGREE_0 = 0
    DEGREE_90 = 90
    DEGREE_180 = 180
    DEGREE_270 = 270

    def __init__(self,parent=None,thin=False):
        super(ImageView,self).__init__(parent)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.spin_scale = newSpinbox((10,500),100,10)
        self.spin_scale.setMaximumWidth(100)
        scroll = add_scroll(self.label)
        layout = QVBoxLayout()
        addWidgets(layout,[scroll])
        self.setLayout(layout)
        if thin:
            self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowTitleHint) 
        # 
        action = partial(newAction,self)
        load = action("Load image",self.load)
        style = action("Set style",self.set_style)
        set_image_size = action("Set image size",self.setImageSize)

        s = ["%d"%i+"%" for i in range(50,325,25)]
        size = QMenu("Zoom",self)
        actions = [QAction(a,self,checkable=True,checked=a==s[0]) for a in s]
        group = QActionGroup(size)
        for a in actions:
            size.addAction(a)
            group.addAction(a)
        group.setExclusive(True)
        group.triggered.connect(self.set_scale)

        s = ["%d"%(i*90) for i in range(0,4)]
        rotation = QMenu("Rotation",self)
        actions = [QAction(a,self,checkable=True,checked=a==s[0]) for a in s]
        group_rot = QActionGroup(rotation)
        for a in actions:
            rotation.addAction(a)
            group_rot.addAction(a)
        group_rot.setExclusive(True)
        group_rot.triggered.connect(self.set_rotation)

        add_context_menu(self,self.label,[load,style,set_image_size,size,rotation])
        # 
        self.size = (640,480)
        self.resize = True
        self.style = ""
        self.scale = 1
        self.degree = self.DEGREE_0
        self.camera_string = "Webcam,0"
        self.camera = None
        self.mat = None
        pass

    def set_rotation(self,act):
        self.degree = int(act.text())
        pass

    def set_scale(self,act):
        s = act.text().split("%")[0]
        self.scale = int(s)/100
    
    def get_scale(self):
        # val = self.spin_scale.value()
        # scale = val/100
        # return self.scale
        pass

    def setImageSize(self, action):
        dlg = BoxEditLabel("Image size",self)
        size = dlg.popUp("%d,%d"%self.size,["640,480","1080,720",
                                            "1280,960",
                                            "480,640","720,1080",
                                            "960,1280"])
        if size:
            try:
                self.size = tuple(str2ListInt(size))
            except:
                self.size = (640,480)
                pass
        pass

    def setResizeEnable(self, action):
        cmd = action.text()
        if cmd == "Enable":
            self.resize = True
        else:
            self.resize = False

    def showMat(self,mat):
        # scale = self.get_scale()
        if self.scale != 1:
            w,h = self.size
            s = (int(w*self.scale),int(h*self.scale))
            m = cv2.resize(mat,s)
            # self.label.setPixmap(ndarray2pixmap(m))
        else:
            m = cv2.resize(mat,self.size)
            # self.label.setPixmap(ndarray2pixmap(m))
        if self.degree != self.DEGREE_0:
            m = im_rotated(m,self.degree)
        self.label.setPixmap(ndarray2pixmap(m))
        pass
    
    def load(self):
        path = get_file_name_dialog(self)
        if path:
            self.load_file(path)
        pass

    def load_file(self,path):
        mat = cv2.imread(path,cv2.IMREAD_UNCHANGED)
        if mat is not None:
            self.showMat(mat)
        pass

    def set_style(self):
        dlg = BoxEditLabel()
        style = dlg.popUp(self.style,[
            "background:gray",
            "background:gray;border-width:3px;border-style:outset;border-color:gray;border-radius:10px",
        ])
        if style :
            self.label.setStyleSheet(style)
            self.style = style
        pass

class MyLabel(QLabel):
    '''label display pixmap'''
    def __init__(self, style=""):
        super().__init__()
        self.setScaledContents(True)
        # self.setAlignment(Qt.AlignCenter)
        if style:
            self.setStyleSheet(style)

class MyButton(QPushButton):
    '''Button expanding'''
    def __init__(self, text="", slot=None, style="", icon="", icon_size=16):
        super().__init__(text)
        if style:
            self.setStyleSheet(style)
        if icon:
            self.setIcon(newIcon(icon))
            self.setIconSize(QSize(icon_size, icon_size))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if slot is not None:
            self.clicked.connect(slot)

def load_label(path):
    lines = []
    try:
        with open(path,"r") as ff:
            lines = ff.readlines()
            ff.close()
        return [l.strip("\n") for l in lines]
    except:
        pass
    return lines

def sorting_pair(l1,l2,key,reverse=False):
    a = list(zip(*sorted(zip(l1, l2),key=key,reverse=reverse)))
    if len(a):
        return list(a[0]),list(a[1])
    else:
        return l1,l2

def write_log(listwidget,log,color=None):
    if listwidget.count() > 100:
        listwidget.clear()
    log = "%s : %s"%(getStrTime(),str(log))
    listwidget.insertItem(0,log)
    if color is not None:
        # n = listwidget.count()
        listwidget.item(0).setForeground(color)

def set_background(w,qcolor):
    p = w.palette() 
    p.setColor(w.backgroundRole(),qcolor) 
    w.setPalette(p)
    return w

def newLabel(text, style="", align=None):
    lb = QLabel(text)
    if style:
        lb.setStyleSheet(style)
    if align:
        lb.setAlignment(align)
    return lb

def newTabWidget(parent=None,position=QTabWidget.North):
    tab = QTabWidget(parent)
    tab.setTabPosition(position)
    tab.setMovable(True)
    return tab

def addTabs(tab,widgets,names,icons=None):
    if icons is not None:
        for w,name,ico in zip(widgets,names,icons):
            tab.addTab(w,newIcon(ico),name)
    else:
        for w,name in zip(widgets,names):
            tab.addTab(w,name)

#=============
def add_context_menu(parent,widget,actions, popup_function=None):
    menu = QMenu(parent)
    addActions(menu,actions)
    widget.setContextMenuPolicy(Qt.CustomContextMenu)
    if popup_function is None:
        widget.customContextMenuRequested.connect(lambda: menu.exec_(QCursor.pos()))
    else:
        widget.customContextMenuRequested.connect(popup_function)
    return menu
#=======================

class ExportDialog(QDialog):
    def __init__(self,parent=None):
        super(ExportDialog,self).__init__(parent)
        self.setWindowTitle("Export")
        self.setGeometry(QRect(100,50,300,600))
        layout = QVBoxLayout()
        bb = BB(BB.Ok|BB.Cancel)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)
        self.export = QPlainTextEdit(self)
        addWidgets(layout,[self.export,bb])
        self.setLayout(layout)

    def popUp(self,text=""):
        self.export.setPlainText(text)
        self.move(QCursor().pos())
        self.show()


class BoxLabel(QDialog):
    def __init__(self,title="New Model",parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        
        bb = BB(BB.Ok|BB.Cancel)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)
        self.ln_name = QLineEdit()
        self.ln_name.setFocus()

        layout = QFormLayout(self)
        layout.addRow("Name", self.ln_name)
        layout.addRow("", bb)

    def popUp(self, bMove=False):
        text = "edit name here"
        self.ln_name.setText(text)
        self.ln_name.setSelection(0, len(text))
        if bMove:
            self.move(QCursor.pos())
        return self.ln_name.text() if self.exec_() else ""


class BoxEditLabel(QDialog):
    def __init__(self,title="QDialog",parent=None):
        super(BoxEditLabel,self).__init__(parent)
        self.setStyleSheet("QLineEdit{background:yellow;font:bold 24px}")
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        bb = BB(BB.Ok|BB.Cancel)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)
        self.ln_name = QLineEdit()
        self.ln_name.setFocus()
        self.list_name = QListWidget()
        addWidgets(layout,[self.ln_name, bb, self.list_name])
        self.setLayout(layout)
        self.list_name.itemClicked.connect(self.itemClicked)
        self.list_name.itemDoubleClicked.connect(self.itemDoubleClicked)

    def itemClicked(self,item):
        self.ln_name.setText(item.text())
        pass

    def itemDoubleClicked(self,item):
        self.ln_name.setText(item.text())
        self.accept()
        pass

    def popUp(self,text="",names=[],bMove=False):
        self.list_name.clear()
        self.list_name.addItems(names)
        self.ln_name.setText(text)
        self.ln_name.setSelection(0,len(text))
        if bMove:
            self.move(QCursor.pos())
        return self.ln_name.text() if self.exec_() else ""

def create_resources():
    cwd = os.getcwd()
    folder = "resources/icon"
    files = os.listdir(folder)
    top =["<!DOCTYPE RCC><RCC version=\"1.0\">","<qresource>"]
    bot = ["</qresource>","</RCC>"]
    for f in files:
        base,ext = get_extenstion_file(f)
        alias = f"<file alias=\"%s\">icon/%s</file>"%(base,f)
        top = top + [alias]
    resources = "\n".join(top + bot)
    with open("resources/resources.qrc","w") as ff:
        ff.write(resources)
        ff.close()
    
    os.system("pyrcc5 -o libs/resources.py resources/resources.qrc")

def format_ex(ex):
    a = "{0}".format(ex).split(":")
    if len(a) > 1:
        error = a[1]
    else:
        error = ""
    dtype = a[0]
    his = {"Exception":[dtype],"Error":[error]}
    return his

class PandasModel(QAbstractTableModel):

    def __init__(self, data):
        super(PandasModel,self).__init__()
        self._data = data
        self.error_data = False
        self.enable_edit = False

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def flags(self, index):
        if self.enable_edit:
            return Qt.ItemIsEnabled|Qt.ItemIsEditable
        return Qt.ItemIsEnabled

    def data(self, index, role):
        if index.isValid():
            data = self._data.iloc[index.row(), index.column()]
            if role in [Qt.DisplayRole, Qt.EditRole]:
                return str(data)
            # if role == Qt.DisplayRole:
            #     return str(self._data.iloc[index.row(), index.column()])
            if self.error_data: 
                return QBrush(QColor(255,0,0,128)) 
        return None
    
    # def setData(self, index, value, role):
    #     if role == Qt.EditRole:
    #         self._data.iloc[index.row(), index.column()] = value
    #         self.dataChanged.emit(index, index)
    #         return True
    #     return False

    # def headerData(self, col, orientation, role):
    #     if orientation == Qt.Horizontal and role == Qt.DisplayRole:
    #         return self._data.columns[col]
    #     return None

def creat_scroll(widget):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(widget)
    return scroll

def add_dock(parent,text,widget,orient=Qt.RightDockWidgetArea,feature=QDockWidget.NoDockWidgetFeatures):
    dock = QDockWidget(text, parent)
    dock.setAllowedAreas(Qt.AllDockWidgetAreas)
    dock.setFeatures(feature)
    dock.setWidget(widget)
    parent.addDockWidget(orient,dock)
    return dock

def add_scroll(widget):
    scroll = QScrollArea()
    scroll.setWidget(widget)
    scroll.setWidgetResizable(True)
    return scroll

def get_extenstion_file(path):
    base = os.path.basename(path)
    return os.path.splitext(base)

def try_exception(do_something,logfile):
    pass
    # except IndexError as ex:
        #     ext = "IndexError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)
        # except ZeroDivisionError as ex:
        #     ext = "ZeroDivisionError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)
        # except KeyError as ex:
        #     ext = "KeyError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)
        # except IOError as ex:
        #     ext = "IOError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)
        # except ValueError as ex:
        #     ext = "ValueError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)
        # except EOFError as ex:
        #     ext = "EOFError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)
        # except SyntaxError as ex:
        #     ext = "SyntaxError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)
        # except TypeError as ex:
        #     ext = "TypeError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)
        # except FileNotFoundError as ex:
        #     ext = "FileNotFoundError {0}".format(ex)
        #     my_except.append(ext)
        #     print(ext)

def generateColorByText(text):
    s = text
    hashCode = int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16)
    r = int((hashCode / 255) % 255)
    g = int((hashCode / 65025)  % 255)
    b = int((hashCode / 16581375)  % 255)
    return QColor(r, g, b)

def save_json(filename,data):
    try:
        with open(filename,"w") as ff:
            data_store = json.dumps(data,sort_keys=True,indent=4)
            ff.write(data_store)
            ff.close()
        return True
    except Exception as ex:
        print("save_json {0}".format(ex))
        return False
    
    pass
def load_json(filename):
    data = {}
    try:
        with open(filename) as ff:
            data = json.load(ff)
            ff.close()
    except Exception as ex:
        print("load_json {0}".format(ex))
    return data

def ptInrect(pos,r):
    x,y = pos
    if r[0] < x < r[0]+r[2] and r[1] < y < r[1]+r[3]:
        return True
    else:
        return False

def exists(f):
    return os.path.isfile(f)

def toInt(v):
    return [int(a) for a in v]

def get_save_file_name_dialog(parent,base="", _filter_="Image files (*png *jpg *bmp)"):
    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    filename,_ = QFileDialog.getSaveFileName(parent,"Seve as",base, _filter_,options=options)
    return filename

def get_folder_name_dialog(parent,base=""):
    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    options |= QFileDialog.ShowDirsOnly
    folder 	= QFileDialog.getExistingDirectory(parent,"Select folder",base,options=options)
    return folder

def get_file_name_dialog(parent,base="",_filter_="Image files (*png *jpg *bmp)"):
    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog
    filename,_ = QFileDialog.getOpenFileName(parent,"Select file",base
            ,_filter_,options=options)
    return filename

def CPU_RAM():
    d = dict(psutil.virtual_memory()._asdict())
    cpu = psutil.cpu_percent()
    # psutil.virtual_memory()

    total = d["total"]
    used = d["used"]

    phycial_memory = used/total*100

    return (cpu,phycial_memory)

def get_gpus():
    try:
        gpus = GPUtil.getGPUs()
        return gpus
    except:
        return []

def get_hardware_resoures():
    resources = {"cpu":{}, "gpu":{}, "ram": {}}

    resources["cpu"]["percent"] = psutil.cpu_percent(interval=1)
    resources["ram"]["percent"] = psutil.virtual_memory().percent

    gpus = get_gpus()
    resources["gpus"] = {}
    for i, gpu in enumerate(gpus):
        resources["gpus"][i] = {}
        resources["gpus"][i]["name"] = gpu.name
        resources["gpus"][i]["percent"] = gpu.load
        resources["gpus"][i]["temperature"] = gpu.temperature
    
    return resources

def loadConfig(filename):
    cfg = ConfigParser()
    cfg.read(filename)
    return cfg

def saveConfig(filename,config):
    with open(filename,"w") as ff:
        config.write(ff)
        ff.close()

class WindowMixin(object):

    def menu(self, title, actions=None)->QMenu:
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None,orient=Qt.TopToolBarArea):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(orient, toolbar)
        return toolbar

class ToolBar(QToolBar):

    def __init__(self, title):
        super(ToolBar, self).__init__(title)
        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        self.setContentsMargins(*m)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def addAction(self, action):
        if isinstance(action, QWidgetAction):
            return super(ToolBar, self).addAction(action)
        btn = ToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        self.addWidget(btn)


class ToolButton(QToolButton):
    """ToolBar companion class which ensures all buttons have the same size."""
    minSize = (25,20)
    def minimumSizeHint(self):
        ms = super(ToolButton, self).minimumSizeHint()
        w1, h1 = ms.width(), ms.height()
        w2, h2 = self.minSize
        ToolButton.minSize = max(w1, w2), max(h1, h2)
        return QSize(*ToolButton.minSize)

class struct(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def readline(filename):
    if not exists(filename):
        return []
    txts = []    
    f = open(filename, "r")
    for x in f:
        x = x.strip().strip("\n")
        txts.append(x)
    return txts

def getStrDateTime():
    return time.strftime("%d%m%y_%H%M%S")

def getStrTime():
    return time.strftime("%H:%M:%S")

def str2int(s):
    try:
        return int(s)
    except:
        return 0

def str2float(s):
    try:
        return float(s)
    except:
        return 0.

def str2ListInt(string):
    lst = string.split(",")
    return [str2int(l) for l in lst]

def str2ListFloat(string):
    lst = string.split(",")
    return [str2float(l) for l in lst]

def addItems(cbb,items):
    [cbb.addItem(it) for it in items if it]

def newBB(parent):
    bb = BB(BB.Ok|BB.Cancel)
    bb.rejected.connect(parent.reject)
    bb.accepted.connect(parent.accept)
    return bb

def newToolButton(action,parent=None):
    b = QToolButton(parent)
    b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    b.setDefaultAction(action)
    return b

def newDialogButton(parent,texts,slots,icons,orient=Qt.Vertical):
    bb = QDialogButtonBox(orient, parent)
    for txt,slot,icon in zip(texts,slots,icons):
        but = bb.addButton(txt,QDialogButtonBox.ApplyRole)
        but.setToolTip(txt)
        if slot is not None:
            but.clicked.connect(slot)
        if icon is not None:
            but.setIcon(newIcon(icon))
    return bb

def newRadioButton(text,slot=None, state=False):
    rad = QRadioButton(text)
    if slot is not None:
        rad.clicked.connect(slot)
    rad.setChecked(state)
    return rad

def newSlider(_range=(0,255),value=0,step=1,slot=None):
    sl = QSlider(Qt.Horizontal)
    a,b = _range
    sl.setRange(a,b)
    sl.setValue(value)
    sl.setSingleStep(step)
    if slot is not None:
        sl.valueChanged.connect(slot)
    return sl

def newDoubleSpinbox(range_,value,step=1,slot=None):
    sp = QDoubleSpinBox()
    sp.setValue(value)
    a,b = range_
    sp.setRange(a,b)
    sp.setSingleStep(step)
    if slot:
        sp.valueChanged.connect(slot)
    return sp

def newSpinbox(range_,value,step=1,slot=None):
    sp = QSpinBox()
    a,b = range_
    sp.setRange(a,b)
    sp.setValue(value)
    sp.setSingleStep(step)
    if slot:
        sp.valueChanged.connect(slot)
    return sp

def newCheckBox(text, slot=None, state=False, tooltip=""):
    ch = QCheckBox(text)
    ch.setChecked(state)
    if slot is not None:
        ch.stateChanged.connect(slot)
    if tooltip:
        ch.setToolTip(tooltip)
    return ch
    
def newIcon(icon):
    return QIcon(':/' + icon)

def addActions(menu,actions):
    for act in actions:
        if isinstance(act,QAction):
            menu.addAction(act)
        else:
            menu.addMenu(act)

def newCbb(items, parent=None, slot=None):
    cbb = QComboBox(parent)
    [cbb.addItem(str(item)) for item in items]
    if slot is not None:
        cbb.activated.connect(slot)
        # cbb.setCurrentIndex()
    return cbb
def newButton(text, parent=None, slot=None,icon=None,enabled=True):
    b = QPushButton(text, parent)
    if slot is not None:
        b.clicked.connect(slot)
    if icon is not None:
        b.setIcon(newIcon(icon))
    # b.setFocus(False)
    b.setEnabled(enabled)
    
    return b

def new_hlayout(widgets=[], stretchs=[], parent=None):
    h = QHBoxLayout(parent)
    addWidgets(h, widgets, stretchs)
    return h

def new_vlayout(widgets=[], stretchs=[], parent=None):
    h = QVBoxLayout(parent)
    addWidgets(h, widgets, stretchs)
    return h

def addWidgets(layout,wds,stretchs=[]):
    for i,w in enumerate(wds):
        if isinstance(w,QWidget):
            layout.addWidget(w)
        else:
            layout.addLayout(w)
        if stretchs:
            if isinstance(layout, QSplitter):
                layout.setStretchFactor(i,stretchs[i])
            else:
                layout.setStretch(i,stretchs[i])

def addTriggered(action,trigger):
    action.triggered.connect(trigger)

def newAction(parent,text,slot=None,shortcut=None,icon=None,tooltip=None,enabled=True):
    a = QAction(text,parent)
    if icon is not None:
        a.setIcon(newIcon(icon))
    if shortcut is not None:
        a.setShortcut(shortcut)
    if slot is not None:
        a.triggered.connect(slot)
    if tooltip is not None:
        a.setToolTip(tooltip)
    a.setEnabled(enabled)
    return a

class ListWidget(QListWidget):
    def __init__(self,style=None,parent=None):
        super(ListWidget,self).__init__(parent)
        if style is not None:
            self.setStyleSheet(style)

        clear = newAction(self,"clear",self.clear,"ctrl+x")
        self.menu = add_context_menu(self,self,[clear])

    def addLog(self, log, color=None, reverse=False):
        if self.count() > 1000:
            self.clear()
        log = "%s : %s"%(getStrTime(),str(log))
        if reverse:
            self.insertItem(0,log)
            if color is not None:
                self.item(0).setForeground(color)
        else:
            self.addItem(log)
            n = self.count()
            if color is not None:
                self.item(n-1).setForeground(color)
        pass

class TableWidget(QTableWidget):
    def __init__(self,headers=[],style=None,parent=None):
        super(TableWidget,self).__init__(parent)
        if style is not None:
            self.setStyleSheet(style)
        
        self.setColumnCount(len(headers))
        # self.setRowCount(1)
        self.setHorizontalHeaderLabels(headers)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def addRow(self, data):
        n_row = self.rowCount()
        self.setRowCount(n_row + 1)
        for i in range(len(data)):
            self.setItem(n_row, i, QTableWidgetItem(str(data[i])))
        pass

    def newItem(self,text,color=None):
        it = QTableWidgetItem(str(text))
        if color is not None:
            it.setForeground(color)
        return it

    def addLog(self,table={},start_row=0,color=None):
        for col,key in enumerate(table.keys()):
            data = table[key]
            for i,x in enumerate(data):
                self.setItem(start_row+i,col,self.newItem(x,color))
        pass

def mkdir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def runThread(target,args=()):
    thread = threading.Thread(target=target,args=args)
    thread.start()

def send_cmd(cmd):
    os.system(cmd)

def pixmap2ndarray(pixmap):
    qimage = pixmap.toImage()
    cvMat  = rgb_view(qimage)[:,:,::-1]
    return cvMat
    
def ndarray2pixmap(arr):
    if len(arr.shape) == 2:
        # qpix = QPixmap.fromImage(ImageQt.ImageQt(misc.toimage(arr)))
        # pixmap = QPixmap.fromImage(gray2qimage(arr))
        rgb = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
    else:
        # channel = arr.shape[-1]
        rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        # qim = QImage(rgb.data,w,h,channel*w, QImage.Format_RGB888)
        # qpix = QPixmap(qim)
        # pixmap = QPixmap.fromImage(array2qimage(rgb))

    h, w, channel = rgb.shape
    qimage = QImage(rgb.data, w, h, channel*w, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def configProxy2dict(config):
    dict_ = {}
    for key in config.keys():
        dict_[key] = eval(config[key])
    return dict_

def bin2dec(b):
    p = 0
    dec = 0
    r = 0
    n = -1
    while b >= 2:
        r = b % 10
        b = (b - r) // 10
        n += 1
        dec += math.pow(2, n)*r
    dec += math.pow(2, n+1)*b
    return int(dec)


def showImage(image,label,fit_window=True):
    if fit_window:
        width , height  = label.width(),label.height()
        h,w             = image.shape[:2]
        s               = min(width/w,height/h)
        new_w           = int(w*s)
        new_h           = int(h*s)
        new_img         = cv2.resize(image,(new_w,new_h))
        qpix            = ndarray2pixmap(new_img)
        label.setPixmap(qpix)
    else:
        qpix    = ndarray2pixmap(image)
        label.setPixmap(qpix)

    return 1

from functools import wraps
def decorator_dt(f):   
    t0 = time.time()  
    @wraps(f)
    def wrapper(*args, **kwds):
        try:         
            return f(*args, **kwds)
        finally:
            print("time do %s : "%f.__name__,time.time() - t0)
    return wrapper

# @decorator_dt
def im_rotated(mat,deg,scale=0.8):
    return imutils.rotate(mat,deg,scale=scale)

def t_img(mat):
    if len(mat.shape) == 2:
        return mat.T
    else:
        b,g,r = cv2.split(mat)
        bT = b.T
        gT = g.T
        rT = r.T
        return cv2.merge((bT,gT,rT))

# @decorator_dt
def cv_rotated(mat,deg):
    if deg == 90:
        return cv2.flip(t_img(mat),1)
    elif deg == 180:
        return cv2.flip(mat,-1)
    elif deg == 270:
        return cv2.flip(t_img(mat),0)
    pass

def scan_dir(folder):
    '''
    return size(Mb)
    '''
    size = 0
    n = 0
    n_dir = 0
    for path,dirs,files in os.walk(folder):
        # print(path)
        n_dir += len(dirs)
        for f in files:
            fp = os.path.join(path,f)
            n += 1
            try:
                size += os.path.getsize(fp)
            except Exception as ex:
                pass
    
    size = size/1024**2
    # print("dirs : ",n_dir)
    # print("files : ",n)
    # print("size of %s : "%folder,size)
    return size
    pass

if __name__ == "__main__":
    create_resources()
    pass


    
    