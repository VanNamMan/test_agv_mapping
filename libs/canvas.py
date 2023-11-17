from libs.shape import *
from libs.info import Info
from libs.tag_config import TagConfig
from libs.utils import BoxEditLabel,QApplication

# cursor
CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_DRAW_POLYGON = Qt.SizeAllCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor

class Canvas(QWidget):
    mouseMoveSignal = pyqtSignal(QPointF)
    mousePressSignal = pyqtSignal(QPointF)
    newShapeSignal = pyqtSignal(int)
    changeShapeLabelSignal = pyqtSignal(int, str)
    changeShapeColorSignal = pyqtSignal(int, QColor)
    deleteShapeSignal = pyqtSignal(int, TagConfig)
    moveShapeSignal = pyqtSignal(int)
    drawShapeSignal = pyqtSignal(QRectF)
    changeShapeSignal = pyqtSignal(int)
    selectedShapeSignal = pyqtSignal(object)
    zoomSignal = pyqtSignal(float)
    actionSignal = pyqtSignal(str)
    applyConfigSignal = pyqtSignal()
    errorLabelSignal = pyqtSignal()
    def __init__(self, parent=None,
                 bcontext_menu=True,
                 benable_drawing=True,
                 label_path="data/classes.txt"):
        super(Canvas, self).__init__(parent)
        self._font = load_json("resources/static/font.json")
        # self.parent = parent
        self.bcontext_menu = bcontext_menu
        self.picture = None
        # self.picture = QPixmap(1280,1020)
        self.painter = QPainter()
        self.scale = 1
        self.org = QPointF()
        self.moving = False
        self.edit = False
        self.drawing = False
        self.highlight = False
        self.wheel = False
        self.current_pos = QPointF()
        self.current = None
        self.win_start_pos = QPointF()
        self.start_pos = QPointF()
        self.start_pos_moving = QPointF()
        
        self.line1 = [QPointF(),QPointF()]
        self.line2 = [QPointF(),QPointF()]
        self.shapes = []
        self.currentInfo:Info = None
        # self.dict_shapes = {}
        self.idVisible = None
        self.idSelected = None
        self.idCorner = None
        self.benable_drawing = benable_drawing
        self.labels = load_label(label_path)
        self.label_path = label_path
        self.last_label = ""
        self.lock = True
        self.boxEditLabel = BoxEditLabel("Enter shape name",self)
        #========
        self.contextMenu = QMenu()
        action = partial(newAction,self)
        # crop = action("crop image",None,"","crop","crop image")
        # add = action("add to process",lambda:self.emitAction("add"),"","add","add shape to process")
        # remove = action("remove shape",lambda:self.emitAction("remove"),"","remove","remove shape process")
        # load_job = action("load_job",lambda:self.emitAction("load_job"),"","load","load job for shape")
        # add_temp = action("add temp",None,"","add","add temp for temple matching")
        # add_roi = action("add ROI",None,"","add","add ROI for vision checking")
        copy = action("copy",self.copyShape,"","copy","copy shape")
        edit = action("Change shape label ...",self.changeShapeLabel,"","edit","Change shape label")
        delete = action("delete",self.deleteShape,"","delete","delete shape")
        # apply = action("apply config",None,"","apply","apply shape config")
        # apply_all = action("apply all",None,"","apply","apply all shape")
        delete_all = action("delete all",self.delete_all,"","","delete shape")

        zoom_in = action("zoom-in",lambda:self.zoom_manual(1.2),"","zoom_in","Zomm In")
        zoom_out = action("zoom-out",lambda:self.zoom_manual(0.8),"","zoom_out","Zoom Out")
        fit_window = action("fit-window",lambda:self.fit_window(),"","fit_window","Fit Window")
        # disable_drawing = action("Disable drawing",lambda:self.set_benable_drawing(not self.benable_drawing),"","disable","Disable drawing")
        
        self.actions = struct(
            # add_temp = add_temp,
            copy    = copy,
            edit    = edit,
            delete  = delete,
            delete_all = delete_all,
            # crop = crop,
            # apply = apply,
            # apply_all = apply_all
            # disable_drawing = disable_drawing,
            # load_job = load_job
        )
        addActions(self.contextMenu,[])
        self.contextMenu.addSeparator()
        addActions(self.contextMenu,[edit,copy,delete,delete_all])
        self.contextMenu.addSeparator()
        addActions(self.contextMenu,[zoom_in,zoom_out,fit_window])
        # addActions(self.contextMenu,[add,remove,load_job])
        # addActions(self.contextMenu,[disable_drawing])

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popUpMenu)
        #=======
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)
        # ==============

    def set_font(self, font):
        self._font = font

    def get_font(self):
        return self._font

    def set_benable_drawing(self,enable):
        self.benable_drawing = enable
        if self.benable_drawing : 
            self.actions.disable_drawing.setText("Disable drawing")
        else:
            self.actions.disable_drawing.setText("Enable drawing")
            
    def setEnabledActions(self,enable):
        # self.actions.crop.setEnabled(enable)
        # self.actions.add_temp.setEnabled(enable)
        self.actions.copy.setEnabled(enable)
        self.actions.edit.setEnabled(enable)
        self.actions.delete.setEnabled(enable)
        self.actions.delete_all.setEnabled(enable)
        # self.actions.apply.setEnabled(enable)
        # self.actions.apply_all.setEnabled(enable)
        pass

    def popUpMenu(self):
        if self.idSelected is None:
            self.setEnabledActions(False)
        else:
            self.setEnabledActions(True)
        if self.bcontext_menu:
            self.contextMenu.exec_(QCursor.pos())

    def emitAction(self,name):
        self.actionSignal.emit(name)

    def focus_cursor(self):
        cur_pos = self.mapFromGlobal(QCursor().pos())
        return self.transformPos(cur_pos)

    def offset_center(self):
        dx = self.width() - self.picture.width()*self.scale
        dy = self.height()- self.picture.height()*self.scale
        pos = QPointF(dx/2,dy/2)
        self.org = pos
        return pos

    def fit_window(self):
        if self.picture is None:
            return
        self.scale = self.scaleFitWindow()
        self.org = self.offset_center()

    def fit_width(self):
        if self.picture is None:
            return
        self.scale = self.scaleFitWidth()
        self.org = self.offset_center()

    def scaleFitWindow(self):
        e = 2.
        w1 = self.width() - 2
        h1 = self.height() - 2
        a1 = w1/h1
        w2 = self.picture.width()
        h2 = self.picture.height()
        a2 = w2/h2
        return w1/w2 if a2 >= a1 else h1/h2
    
    def scaleFitWidth(self):
        w1 = self.width() - 2
        w2 = self.picture.width()
        a = w1 / w2
        return a

    def zoom_origin(self):
        self.scale = 1
        self.org = QPointF()

    def zoom_manual(self,s):
        self.scale *= s
        self.zoomSignal.emit(self.scale)
        return
    
    def zoom_by_wheel(self,s):
        old_scale = self.scale
        p1 = self.current_pos
        self.scale *= s
        # focus cursor pos
        self.org -= p1*self.scale-p1*old_scale
        # self.repaint()
        self.zoomSignal.emit(self.scale)
        return
    
    def transformPos(self,pos):
        '''
        convert main pos -> cv pos
        '''
        return (pos - self.org)/self.scale 
    
    def transformPosInv(self, pos):
        '''
        convert main pos -> cv pos
        '''
        return pos * self.scale + self.org
    
    def move_org(self,point):
        self.org += point

    def update_center(self,pos):
        pass
    
    def draw_rect(self,pos1,pos2):
        self.current_rect = QRectF(pos1,pos2)
        
    def shape_to_cvRect(self,shape):
        p1 = shape.points[0]
        p2 = shape.points[2]
        x , y = p1.x() , p1.y()
        x2 , y2 = p2.x() , p2.y()
        # 
        x = max(x,0)
        y = max(y,0)
        x2 = min(x2,self.picture.width())
        y2 = min(y2,self.picture.height())
        # 
        w , h = int(x2- x) , int(y2 - y)
        x , y = int(x) , int(y)
        # 
        return (x,y,w,h) 
        
    def changeShapeLabel(self):
        if self.idSelected is not None:
            label = self.boxEditLabel.popUp(self.last_label,self.labels,bMove=True)
            if label:
                self[self.idSelected].label = label
                self.last_label = label
                self.append_new_label(label)

    def copyShape(self):
        if self.idSelected is not None:
            shape = self[self.idSelected].copy()
            self.shapes.append(shape)
            # self.dict_shapes[shape.label] = shape
            i = self.idSelected
            # self.releae_shape_selected(i)
            self.idSelected = i + 1

    def set_shape_selected(self, index):
        for i in range(len(self)):
            if i == index:
                self[index].selected = True
                self.idSelected = index
                self.selectedShapeSignal.emit(index)
            else:
                self[i].selected = False

    def undo(self):
        if len(self.shapes) > 0:
            self.shapes.remove(self[-1])

    def deleteShape(self):
        if self.idSelected is not None:
            # self.emitAction("remove")
            shape = self[self.idSelected]
            self.deleteShapeSignal.emit(self.idSelected, shape.config)
            self.shapes.remove(shape)
            # del(self.dict_shapes[shape.label])

            self.idVisible = self.idSelected = self.idCorner = None

    def delete_all(self):
        for i in range(len(self)):
            self.deleteShapeSignal.emit(len(self)-1, self.shapes[-1].config)
            self.shapes.remove(self.shapes[-1])
        self.idVisible = self.idSelected = self.idCorner = None

    def moveShape(self,i,v):
        if self.picture is None:
            return
        self[i].move(v)
        self.moveShapeSignal.emit(i)
        self.changeShapeSignal.emit(i)

    def append_new_label(self,label):
        if label not in self.labels:
            self.labels.append(label)
            with open(self.label_path,"a") as ff:
                ff.write(label+"\n")
                ff.close()
        pass

    def newShape(self,r,label,config=None):
        labels = [s.label for s in self.shapes]
        if label in labels:
            QMessageBox.warning(self, "WARNING", "Shape already exists")
            return
        
        n = len(self)
        shape = Shape(label)
        if config is None:
            shape.config = TagConfig(name=label)
        else:
            shape.config = config

        shape.shapeColorChanged.connect(self.shape_color_changed)
        shape.shapeLabelChanged.connect(self.shape_label_changed)
        ret, points = shape.get_points(r)

        if ret:
            shape.points = points
            self.shapes.append(shape)
            self.newShapeSignal.emit(n)
            self.last_label = label
            # self.append_new_label(label)
        return shape
    
    def shape_color_changed(self, color:QColor):
        index = self.shapes.index(self.sender())
        self.changeShapeColorSignal.emit(index, color)

    def shape_label_changed(self, label:str):
        index = self.shapes.index(self.sender())
        self.changeShapeLabelSignal.emit(index, label)
    
    def format_shape(self,shape):
        label = shape.label
        r = self.shape_to_cvRect(shape)
        id = self.shapes.index(shape)
        return {
            "label" : label,
            "box" : r,
            "id" : id
        }

    def pos_in_shape(self,pos,shape):
        pass

    def visibleShape(self,pos):
        n = len(self)
        ids_shape_contain_pos = []
        distances = []
        for i in range(n):
            self[i].visible = False
            d = self[i].dis_to(pos)
            if d > 0:
                ids_shape_contain_pos.append(i)
                distances.append(d)

        if len(distances) > 0:
            index = np.argmin(distances)
            self.idVisible = ids_shape_contain_pos[index]
            self[self.idVisible].visible = True
            # self.visi.emit(self.idSelected)
        else:
            self.idVisible = None

        return self.idVisible
    
    def selectedShape(self,pos):
        n = len(self)
        ids_shape_contain_pos = []
        distances = []
        for i in range(n):
            self[i].selected = False
            d = self[i].dis_to(pos)
            if d > 0:
                ids_shape_contain_pos.append(i)
                distances.append(d)

        if len(distances) > 0:
            index = np.argmin(distances)
            self.idSelected = ids_shape_contain_pos[index]
            self[self.idSelected].selected = True
            # self.selectedShapeSignal.emit(self.idSelected)
        else:
            self.idSelected = None
        self.selectedShapeSignal.emit(self.idSelected)

    def highlightCorner(self,pos,epsilon=10):
        if self.idSelected is None:
            return False
        try:
            i = self.idSelected
            return self[i].get_corner(pos,epsilon)        
        except Exception as ex:
            print("{}".format(ex))   
            return False 

    def cancel_edit(self):
        self.edit = False
        self.drawing = False
        self.moving = False
        
    def paintEvent(self, event):
        if self.picture is None:
            return super(Canvas,self).paintEvent(event)
        p = self.painter
        p.begin(self)

        lw = max(int(5 * self.scale), 1)

        p.setPen(QPen(Qt.green, lw))
        p.translate(self.org)
        p.scale(self.scale,self.scale)
        if self.picture:
            p.drawPixmap(0, 0, self.picture)
        
        for shape in self.shapes:
            shape.set_font(self._font)
            shape.paint(p, self.scale)

        if self.currentInfo is not None:
            self.currentInfo.paint(p, self.scale)

        if self.edit :
            # draw center
            pos = self.current_pos
            self.line1 = [QPointF(0,pos.y()),QPointF(self.picture.width(),pos.y())]
            self.line2 = [QPointF(pos.x(),0),QPointF(pos.x(),self.picture.height())]
            p.drawLine(self.line1[0],self.line1[1])
            p.drawLine(self.line2[0],self.line2[1])
        
        if self.drawing :    # draw rect
            if self.current is not None:
                p.drawRect(self.current)

        self.update()
        p.end()

    # def to_shape_font(self, s:Shape):
    #     font = {
    #         "thickness": self._font["thickness"],
    #         "fontsize": self._font["fontsize"],
    #         "radius": self._font["radius"]
    #     }
    #     font["color"] = self._font.get(s.config.table_name, None)
    #     return font
    
    def wheelEvent(self, ev):
        if self.picture is None:
            return super(Canvas,self).wheelEvent(ev)
        delta = ev.angleDelta()
        h_delta = delta.x()
        v_delta = delta.y()
        mods = ev.modifiers()
        if Qt.ControlModifier == int(mods) and v_delta:
            self.zoom_by_wheel(1+v_delta/120*.2)
            pass
        else:
            pos = QPointF(0.,v_delta/8.)
            self.move_org(pos)
            pass
        
        ev.accept()

    def mousePressEvent(self,ev):
        if self.picture is None :
            return super(Canvas,self).mousePressEvent(ev)
        # pos = self.transformPos(ev.pos())
        self.start_pos = self.transformPos(ev.pos())
        if ev.button() == Qt.LeftButton:
            self.mousePressSignal.emit(self.start_pos)
            if self.edit:
                if self.idSelected is not None:
                    self[self.idSelected].selected = False
                    self.idSelected = None
                self.drawing = True
            else:
                self.moving = True
                if not self.highlight:
                    self.selectedShape(self.start_pos)
    
    def mouseReleaseEvent(self,ev):
        if self.picture is None :
            return super(Canvas,self).mouseReleaseEvent(ev)
        # pos = self.transformPos(ev.pos())
        self.move_shape = False
        self.restore_cursor()
        if ev.button() == Qt.LeftButton:
            if self.drawing:
                r = self.current
                if r is not None and r.width() > Shape.MIN_WIDTH and r.height() > Shape.MIN_WIDTH:
                    label = self.boxEditLabel.popUp(self.last_label,self.labels,bMove=False)
                    if label and label not in [s.label for s in self]:
                        self.newShape(r,label)
                    else:
                        self.errorLabelSignal.emit()
                self.current = None
       
            self.cancel_edit()
    
    def mouseMoveEvent(self,ev):
        if self.picture is None :
            return super(Canvas,self).mouseMoveEvent(ev)

        self.current_pos = self.transformPos(ev.pos())
        self.mouseMoveSignal.emit(self.current_pos)
        if self.drawing:
            self.current = QRectF(self.start_pos,self.current_pos)
            self.drawShapeSignal.emit(self.current)
            self.override_cursor(CURSOR_DRAW)
        if not self.moving:
            self.highlight = self.highlightCorner(self.current_pos,epsilon=40)
            if self.highlight:
                pass

        if self.moving:
            v = self.current_pos - self.start_pos

            if self.highlight and not self.lock:
                self[self.idSelected].change(v)

            elif self.idSelected is not None and not self.lock:
                self[self.idSelected].move(v)
                
            else:
                self.move_org(v*self.scale)

            self.start_pos = self.transformPos(ev.pos())
            if self.idSelected is not None:
                self.changeShapeSignal.emit(self.idSelected)

            if self.currentInfo is not None:
                self.currentInfo.move(v)
            self.override_cursor(CURSOR_MOVE)

        if self.visibleShape(self.current_pos) is None and not self.highlight and not self.drawing:
            # 
            self.del_info()
            # 
        elif not self.highlight and not self.drawing and not self.moving:
            self.new_info()
            pass
            # self.override_cursor(CURSOR_GRAB)
        if self.edit :
            # self.restore_cursor()
            pass

    def currentCursor(self):
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            cursor = cursor.shape()
        return cursor
    
    def overrideCursor(self, cursor):
        self._cursor = cursor
        if self.currentCursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)

    def resizeEvent(self,ev):
        if self.picture is None:
            return super(Canvas,self).resizeEvent(ev)
        self.fit_window()
        pass

    def keyPressEvent(self,ev):
        key = ev.key()
        step = 5
        # if key == Qt.Key_1:
        #     self.parent.io_signal = not self.parent.io_signal
        if key == Qt.Key_Q:
            if self.benable_drawing:
                pass

        elif key == Qt.Key_Escape:
            self.edit = False

        elif key == Qt.Key_Return:
            pass

        elif key == Qt.Key_Delete:
            self.deleteShape()
            pass

        i = self.idSelected
        if i is None :
            return
        if key == Qt.Key_Right:
            v = QPointF(step,0)
            self.moveShape(i,v)
        elif key == Qt.Key_Left:
            v = QPointF(-step,0)
            self.moveShape(i,v)
        elif key == Qt.Key_Up:
            v = QPointF(0,-step)
            self.moveShape(i,v)
        elif key == Qt.Key_Down:
            v = QPointF(0,step)
            self.moveShape(i,v)
        
    def show_pixmap_from_other_thread(self,pixmap,fit):
        self.load_pixmap(pixmap,fit)
        pass
    def load_pixmap(self,pixmap,fit=False):
        self.picture = pixmap
        if fit:
            self.fit_window()
        self.zoomSignal.emit(self.scale)
        self.repaint()

    def current_cursor(self):
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            cursor = cursor.shape()
        return cursor

    def override_cursor(self, cursor):
        self._cursor = cursor
        if self.current_cursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)

    def restore_cursor(self):
        QApplication.restoreOverrideCursor()
        # self.setCursor(QCursor(CURSOR_DEFAULT))

    def new_info(self):
        s = self[self.idVisible]
        self.currentInfo = Info(shape=s, topleft=self.current_pos)

    def del_info(self):
        self.currentInfo = None

    def restore_shapes(self, params:dict):
        self.shapes.clear()
        labels = list(params.keys())
        for lb in labels:
            s = Shape()
            s.label = lb
            s.config = params[lb]
            if s.config is not None:
                x, y, w, h = str2ListInt(params[lb]["crop"]["box"])
                s.points = [
                    QPointF(x, y),
                    QPointF(x + w, y),
                    QPointF(x + w, y + h),
                    QPointF(x, y + h)
                ]
                self.shapes.append(s)

    def __len__(self):
        return len(self.shapes)

    def __getitem__(self, key):
        # if isinstance(key,int):
         return self.shapes[key]
        # elif isinstance(key,str):
        #     return self.dict_shapes[key]

    def __setitem__(self, key, value):
        self.shapes[key] = value

    def clear_pixmap(self):
        self.picture = None
        
    def clear(self):
        self.shapes.clear()
        self.idSelected = None
        self.idVisible = None
        self.idCorner = None


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    wd = QMainWindow()
    canvas = Canvas(wd)
    canvas.load_pixmap(QPixmap(640,480))
    wd.setCentralWidget(canvas)
    wd.showMaximized()
    sys.exit(app.exec_())