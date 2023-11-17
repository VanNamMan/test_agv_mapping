from libs.utils import *
from libs.shape import Shape
from libs.tag_config import TagConfig
import numpy as np

# color shape
DEFAULT_FILL_COLOR = QColor(0, 0, 0, 150)
DEFAULT_SELECT_FILL_COLOR = QColor(255, 100,100, 50)
DEFAULT_VISIBLE_FILL_COLOR = QColor(128, 128, 0, 0)
DEFAULT_VERTEX_FILL_COLOR = QColor(255, 255, 255, 0)
DEFAULT_VERTEX_SELECT_FILL_COLOR = QColor(255,255,0, 255)
DEFAULT_SELECT_COLOR = QColor(255,0,0, 255)


class Info(object):
    def __init__(self, shape:Shape = None, topleft=QPoint(0, 0), width=250, height=300):
        super(Info,self).__init__()
        self.points = [
            topleft,
            topleft + QPointF(width, 0),
            topleft + QPointF(width, height),
            topleft + QPointF(0, height),
        ]
        self.selected = False
        self.visible = False
        self.corner = None

        self._config = TagConfig()
        self.set_config(shape.config)
        self.image_debug = None
        # shape parameter 
        self.shape = shape
        self.font = shape.get_font()
        self.scale = 1.
        # 
        self.vertex_fill_color        = DEFAULT_VERTEX_FILL_COLOR
        self.vertex_select_fill_color = DEFAULT_VERTEX_SELECT_FILL_COLOR
        self.fill_color               = DEFAULT_FILL_COLOR
        self.select_color             = DEFAULT_SELECT_COLOR
        self.select_fill_color        = DEFAULT_SELECT_FILL_COLOR
        self.visible_fill_color       = DEFAULT_VISIBLE_FILL_COLOR

    def set_config(self, config:TagConfig):
        self._config = config

    def get_config(self):
        return self._config

    def paint(self,painter,s=1):
        self.scale = s
        color = Qt.green
        lw = max(self.font["thickness"], 1)
        painter.setPen(QPen(color))
        line_path = QPainterPath()
        # vertex_path = QPainterPath()

        line_path.moveTo(self.points[0])

        for i, p in enumerate(self.points):
            line_path.lineTo(p)

        line_path.lineTo(self.points[0])
        #  draw rect
        painter.drawPath(line_path)
        painter.fillPath(line_path, DEFAULT_FILL_COLOR)
        # draw label
        if self._config:
            if self.scale < 1:
                fs = int(10  / self.scale)
            else:
                fs = int(10  * self.scale)
            font = QFont("Arial", fs)
            painter.setFont(font)
            painter.setPen(QPen(Qt.white))

            config:TagConfig = self._config

            n_lines = len(config.columns) + 1
            height = self[2].y() - self[0].y()
            d = int(height // n_lines)

            pos_start = (int(self[0].x() + 5), int(self[0].y() + d))

            columns = config.columns
            values = config.values[:-1]
            lines = [
                (f"{columns[i]}: {values[i]}", (pos_start[0], pos_start[1] + (i + 1) * d))
                for i in range(0, len(values))
            ]
            lines = [(f"Tag: {config.table_name}", (pos_start[0], pos_start[1]))] + lines

            for line in lines:
                text = line[0]
                pos = line[1]

                painter.drawText(pos[0], pos[1], text)

    def translate_(self,v:QPointF):
        self.points = [p + v for p in self.points]
    
    def move(self,v:QPointF):
        self.points = [p + v for p in self.points]
        pass
     
    def copy(self):
        shape = Info(label=self.label+"_copy")
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

        if width > Info.MIN_WIDTH and height > Info.MIN_WIDTH:
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