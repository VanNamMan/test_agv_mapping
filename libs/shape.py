from libs.utils import *
from libs.tag_config import TagConfig
import numpy as np

# color shape
DEFAULT_FILL_COLOR = QColor(128, 128, 255, 100)
DEFAULT_VISIBLE_FILL_COLOR = QColor(255, 255, 0, 100)
DEFAULT_SELECT_FILL_COLOR = QColor(128, 255, 0, 100)
DEFAULT_VERTEX_FILL_COLOR = QColor(255, 255, 255, 0)
DEFAULT_VERTEX_SELECT_FILL_COLOR = QColor(255,0,0, 255)
DEFAULT_SELECT_COLOR = QColor(255,0,0, 255)


class Shape(QObject):
    # RADIUS = 5
    # THICKNESS = 1
    # FONT_SIZE = 10
    shapeColorChanged = pyqtSignal(QColor)
    shapeLabelChanged = pyqtSignal(str)
    MIN_WIDTH = 10
    def __init__(self,label = None):
        super(Shape,self).__init__()
        self.points = []
        self.selected = False
        self.visible  = False
        self.corner   = None
        self._label    = label

        self.image_debug = None
        # shape parameter 
        self._config = TagConfig()
        self.scale = 1.

        self._radius = 5
        self._thickness = 1
        self._font_size = 10
        self._color = QColor(128, 128, 128)
        # 
        # self.vertex_fill_color        = DEFAULT_VERTEX_FILL_COLOR
        # self.vertex_select_fill_color = DEFAULT_VERTEX_SELECT_FILL_COLOR
        # self.fill_color               = DEFAULT_FILL_COLOR
        # self.select_color             = DEFAULT_SELECT_COLOR
        # self.select_fill_color        = DEFAULT_SELECT_FILL_COLOR
        # self.visible_fill_color       = DEFAULT_VISIBLE_FILL_COLOR

    def get_font(self):
        return {
            "thickness": self._thickness,
            "fontsize": self._font_size,
            "radius": self._radius,
            "color": list(self._color.getRgb())
        }

    def set_font(self, font:dict):
        self.set_thickness(font.get("thickness", self._thickness))
        self.set_font_size(font.get("fontsize", self._font_size))
        self.set_radius(font.get("radius", self._radius))

        color = font.get(self.config.table_name, None)
        if color is not None:
            color = QColor(color)
            self.set_color(color)
            self.shapeColorChanged.emit(self.color)

    def set_radius(self, val:int):
        self._radius = val

    def set_font_size(self, val:int):
        self._font_size = val

    def set_thickness(self, val:int):
        self._thickness = val

    def set_color(self, color:QColor):
        self._color = color

    @property
    def color(self):
        return self._color
    
    @property
    def index(self):
        return self._index

    def drawVertex(self, path, i):
        # d = max(int(Shape.RADIUS / self.scale), 10)
        d = self._radius
        point = self.points[i]
        if self.corner is not None and i == self.corner:
            path.addRect(point.x() - d, point.y() - d, 2*d, 2*d)
        elif self.visible:
            path.addEllipse(point, d/2, d/2)
        else:
            path.addEllipse(point, d / 2.0, d / 2.0)
    
    def paint(self,painter,s=1):
        self.scale = s
        fill_color:QColor = self._color
        lw = self._thickness
        painter.setPen(QPen(fill_color, lw))
        line_path = QPainterPath()
        vertex_path = QPainterPath()

        line_path.moveTo(self.points[0])

        for i, p in enumerate(self.points):
            line_path.lineTo(p)
            self.drawVertex(vertex_path,i)

        line_path.lineTo(self.points[0])
        #  draw rect
        painter.drawPath(line_path)

        fill_color.setAlpha(175)
        
        #  fill
        if self.visible or self.corner is not None:
            fill_color.setAlpha(150)
        if self.selected:
            fill_color.setAlpha(75)

        painter.fillPath(line_path, fill_color)

        if self.visible or self.selected:
            color = DEFAULT_VERTEX_SELECT_FILL_COLOR if (self.visible or self.corner is not None) else fill_color
            painter.fillPath(vertex_path, color)

        # draw label
        if self.config.name is not None:
            # fs = max(10 * int(Shape.FONT_SIZE * self.scale), 50)
            fs = self._font_size
            font = QFont("Arial", fs)
            font.setBold(True)

            fm = QFontMetrics(font)

            width = fm.width(self.config.name)
            height = fm.height()

            painter.setFont(font)
            painter.setPen(QPen(Qt.black, lw + 2))

            fill_color.setAlpha(255)

            px = int(self[0].x() + self[2].x()) // 2 - width // 2
            py = int(self[0].y() + self[2].y()) // 2 + height // 2
            painter.drawText(px, py, self.config.name)

    @property
    def config(self):
        return self._config
    
    @config.setter
    def config(self, config:TagConfig):
        self._config = config
        if config.name != self.label:
            self.label = config.name
            self.shapeLabelChanged.emit(self.label)

    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, val:str):
        self._label = val
        self.shapeLabelChanged.emit(self._label)

    def translate_(self,v:QPointF):
        self.points = [p + v for p in self.points]
    
    def move(self,v:QPointF):
        self.points = [p + v for p in self.points]
        pass
     
    def copy(self):
        shape = Shape(label=self.label+"_copy")
        shape.points = self.points
        shape.visible = self.visible
        shape.corner = self.corner
        shape.config = self.config
        shape.translate_(QPointF(50.,50.))
        return shape

    def contain(self,pos):
        x,y = pos.x() , pos.y()
        tl = self.points[0]
        br = self.points[2]
        x1,y1 = tl.x() , tl.y()
        x2,y2 = br.x() , br.y()
        return x1 < x < x2 and y1 < y < y2

    def get_corner(self,pos,epsilon=10):
        for i in range(len(self.points)):
            d = self.distance(pos,self.points[i])
            if d < epsilon:
                self.corner = i
                return True
        self.corner = None
        return False

    def distance(self,p1,p2):
        p = p2 - p1
        return np.sqrt(p.x()**2+p.y()**2)

    def dis_to(self,pos):
        x,y = pos.x() , pos.y()
        tl = self.points[0]
        br = self.points[2]
        dx = min([np.abs(x - tl.x()),np.abs(x - br.x())])
        dy = min([np.abs(y - tl.y()),np.abs(y - br.y())])
        if self.contain(pos):
            return min(dx,dy)
        else:
            return -min(dx,dy)

    def change(self,v):
        points = self.points
        corner = self.corner
        R = QRectF(self.points[0],self.points[2])
        pos = self.points[corner] + v

        if corner == 0:
            R.setTopLeft(pos)
        elif corner == 1:
            R.setTopRight(pos)
        elif corner == 2:
            R.setBottomRight(pos)
        elif corner == 3:
            R.setBottomLeft(pos)
        
        ret, points = self.get_points(R)
        if ret:
            self.points = points

    def get_points(self,r = QRectF()):
        pos1 = r.topLeft()
        pos2 = r.topRight()
        pos3 = r.bottomRight()
        pos4 = r.bottomLeft()

        width = pos3.x() - pos1.x()
        height = pos3.y() - pos1.y()

        if width > Shape.MIN_WIDTH and height > Shape.MIN_WIDTH:
            ret = True
        else:
            ret = False
        return ret, [pos1,pos2,pos3,pos4]    

    @property
    def cvBox(self):
        tl = self.points[0]
        br = self.points[2]
        x, y = tl.x(), tl.y()
        w, h = br.x() - x, br.y() - y

        x, y, w, h = list(map(int, [x, y, w, h]))
        x = max(x, 0)
        y = max(y, 0)
        return [x, y, w, h]
    
    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __setitem__(self, key, value):
        self.points[key] = value


if __name__ == "__main__":
    pass