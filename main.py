
from ui.main_ui import Ui_MainWindow
from libs.mywidget import *
from libs.tag_config import TagConfig
from libs.canvas import Canvas
from libs.shape import Shape
from libs.utils import *
create_resources()
from libs.constant import *
import libs.database_lite as db
from libs import resources
from server import Server

mkdir(DATABASE_DIR)

class MainWindow(QMainWindow, WindowMixin):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.canvas = Canvas(self, label_path="resources/static/labels.txt")
        layout = QVBoxLayout(self.ui.centralwidget)
        addWidgets(layout, [add_scroll(self.canvas)])

        self.configDlg = ConfigDlg(self)
        self.listShapeDlg = ListShapeDlg(self)
        self.fontDlg = FontDlg()

        add_dock(self, "Config", self.configDlg, feature=QDockWidget.AllDockWidgetFeatures)
        add_dock(self, "Shapes", self.listShapeDlg, feature=QDockWidget.AllDockWidgetFeatures)

        pixmap = QPixmap("image.jpg")
        self.canvas.load_pixmap(pixmap, True)

        self.create_signals_slots()
        self.create_toolbar()
        self.create_db()
        self.load()
        self.create_server()

    def create_server(self):
        self.server = Server(
            host="localhost",
            port=8000
        )
        self.server.dataSignal.connect(self.recv_from_client)
        if not self.server.error:
            self.server.run()
        else:
            QMessageBox.warning(self, "Warning", f"Server create error: {self.server.error}")

    def create_toolbar(self):
        action = partial(newAction, self)
        drawAction = action("Draw", self.action_triggered, "q", "draw", "Create rectangle")
        fitWidth = action("Fit Width", self.action_triggered, "ctrl+\\", "fit_width", "Fit Width")
        fitWindow = action("Fit Window", self.action_triggered, "ctrl+=", "fit_window", "Fit Window")
        zoomIn = action("Zoom In", self.action_triggered, "ctrl++", "zoom_in", "Zoom In")
        zoomOut = action("Zoom Out", self.action_triggered, "ctrl+-", "zoom_out", "Zoom Out")

        fontAction = action("Font And Color", self.action_triggered, "", "font_color", "Set Font Shape")

        saveAction = action("Save", self.action_triggered, "ctrl+s", "save", "Save all tags")
        openAction = action("Open", self.action_triggered, "ctrl+o", "open_file", "Open image file")

        self.ch_lock = newCheckBox("Lock Change Shape", self.lock_change_shape, True, 
                                   "Khóa thay đổi vị trí và kích thước khu vực")
        
        shortcutAction = action("Shortcut", self.action_triggered, "", "", "Show shortcut")

        self.actions = struct(
            drawAction=drawAction,
            fitWidth=fitWidth,
            fitWindow=fitWindow,
            zoomIn=zoomIn,
            zoomOut=zoomOut,
            fontAction=fontAction,
            saveAction=saveAction,
            openAction=openAction,
            shortcutAction=shortcutAction
        )
        self.toolbar("Font", [fontAction])
        self.toolbar("Zoom Tools", [fitWidth, fitWindow, zoomIn, zoomOut])
        tools = self.toolbar("Drawing Tools", [drawAction])
        tools.addWidget(self.ch_lock)

        self.menu("File", [openAction, saveAction])
        self.menu("Canvas Tools", [drawAction, fitWidth, fitWindow, zoomIn, zoomOut])
        self.menu("Help", [shortcutAction])
        pass

    def create_signals_slots(self):
        self.configDlg.applyAction.triggered.connect(self.action_triggered)
        self.configDlg.saveAction.triggered.connect(self.action_triggered)

        self.canvas.mouseMoveSignal.connect(self.mouse_move)
        self.canvas.newShapeSignal.connect(self.new_shape)
        self.canvas.deleteShapeSignal.connect(self.del_shape)
        self.canvas.changeShapeSignal.connect(self.change_shape_coordinates)
        self.canvas.changeShapeLabelSignal.connect(self.change_shape_label)
        self.canvas.changeShapeColorSignal.connect(self.change_shape_color)
        self.canvas.selectedShapeSignal.connect(self.shape_selected)
        self.canvas.errorLabelSignal.connect(self.shape_error_label)

        self.listShapeDlg.itemSelectionChanged.connect(self.item_shape_select_change)

    def action_triggered(self):
        if self.sender() == self.actions.drawAction:
            self.canvas.edit = True

        elif self.sender() == self.actions.fitWidth:
            self.canvas.fit_width()

        elif self.sender() == self.actions.fitWindow:
            self.canvas.fit_window()

        elif self.sender() == self.actions.zoomIn:
            self.canvas.zoom_manual(1.2)
        
        elif self.sender() == self.actions.zoomOut:
            self.canvas.zoom_manual(0.8)

        elif self.sender() == self.actions.fontAction:
            self.set_canvas_font()

        elif self.sender() == self.actions.openAction:
            self.open_file()

        elif self.sender() == self.actions.saveAction:
            self.save()

        elif self.sender() == self.configDlg.applyAction:
            self.apply()

        elif self.sender() == self.configDlg.saveAction:
            self.save()

        elif self.sender() == self.actions.shortcutAction:
            self.show_shortcut()

    def show_shortcut(self):
        ShortcutDlg(self).showNormal()

    def recv_from_client(self, data:str):
        '''
        data: "x,y"
        '''
        x, y = data.split(",")
        self.configDlg.ui.ln_x.setText(x)
        self.configDlg.ui.ln_y.setText(y)

    def lock_change_shape(self):
        if self.ch_lock.isChecked():
            self.canvas.lock = True
        else:
            self.canvas.lock = False

    def set_canvas_font(self):
        cur_font = self.canvas.get_font()
        font = self.fontDlg.popup(cur_font)
        if font is not None:
            self.canvas.set_font(font)
            save_json("resources/static/font.json", font)            

    def item_shape_select_change(self):
        index = self.listShapeDlg.currentRow()
        self.canvas.set_shape_selected(index)

    def open_file(self):
        path = get_file_name_dialog(self)
        if path:
            self.open_file_path(path)

    def open_file_path(self, path):
        self.canvas.load_pixmap(QPixmap(path), True)

    def apply(self):
        if not self.configDlg.current_tag():
            QMessageBox.warning(self, "Cảnh báo", "Hãy chọn loại thẻ")
            return
        index = self.canvas.idSelected
        if index is not None:
            config = self.configDlg.get()
            self.canvas[index].config.change(**config)

    def shape_error_label(self):
        QMessageBox.warning(self, "Cảnh báo", "Tên khu vực không trùng lặp và không để trống")

    def change_shape_color(self, index, color):
        self.listShapeDlg.change_item_shape(index=index, color=color)

    def change_shape_label(self, index, label):
        self.listShapeDlg.change_item_shape(index=index, text=label)

    def change_shape_coordinates(self, index):
        x, y, w, h = self.canvas[index].cvBox
        coordinates = "%d,%d,%d,%d" % (x, y, w, h)
        self.canvas[index].config["coordinates"] = coordinates
        self.canvas.set_shape_selected(index)

    def del_shape(self, index:int, config:TagConfig):
        if index is not None:
            config.delete_db()
            self.listShapeDlg.remove_item_shape(index)

    def new_shape(self, index):
        if index is not None:
            x, y, w, h = self.canvas[index].cvBox
            coordinates = "%d,%d,%d,%d" % (x, y, w, h)
            self.canvas[index].config["name"] = self.canvas[index].label
            self.canvas[index].config["coordinates"] = coordinates
            self.listShapeDlg.add_item_shape(self.canvas[index])
            self.canvas.set_shape_selected(index)

    def shape_selected(self, index=None):
        if index is None:
            self.configDlg.set_editable(False)
        else:
            self.configDlg.set_editable(True)
            self.configDlg.set(self.canvas[index].config)
            self.listShapeDlg.setCurrentRow(index)

    def mouse_move(self, point:QPointF):
        # pos = self.canvas.transformPosInv(point)

        # pos = QPoint(x, y)
        # pos = self.mapToGlobal(pos)

        # self.cfg_dlg.show_visible(pos)

        msg = "point(%d, %d)" % (point.x(), point.y())
        self.statusBar().showMessage(msg)

    def save(self):
        s:Shape = None
        config:TagConfig = None

        error = ""
        for s in self.canvas.shapes:
            config = s.config
            if config.table_name:
                if config.is_insert_in_db():
                    if config.is_key_change():
                        ret, error = config.delete_db()
                        if ret:
                            ret, error = config.insert_db()
                    else:
                        ret, error = config.update_db()
                else:
                    ret, error = config.insert_db()
        if not error:
            QMessageBox.information(self, "Information", "Save success")
        else:
            QMessageBox.warning(self, "Warning", f"Save failed: {error}")

        self.ch_lock.setChecked(True)

    def load(self):
        # sql = "select * from transfer"
        conn = db.create_db(DATABASE_PATH)
        table_names = []
        if conn:
            try:
                sql = f'select name from sqlite_schema where name not like "sqlite_%"'
                table_names = [t[0] for t in conn.execute(sql).fetchall()]
            except Exception as ex:
                sql = f'select name from sqlite_master where name not like "sqlite_%"'
                table_names = [t[0] for t in conn.execute(sql).fetchall()]
            finally:
                pass

        self.canvas.shapes.clear()
        s:Shape = None

        for tb in table_names:
            sql = f"select * from {tb}"
            rows = db.select(conn, sql)

            sql = f'select name from pragma_table_info("{tb}")'
            columns = [c[0] for c in conn.execute(sql).fetchall()]
    
            for r in rows:
                self.add_new_shape_from_row(r, columns, tb)

    def cvt_str_to_points(self, strbox:str):
        x, y, w, h = list(map(int, strbox.split(",")))
    
        points = [
            QPoint(x, y),
            QPoint(x + w, y),
            QPoint(x + w, y + h),
            QPoint(x, y + h)
        ]
        return points

    def cvt_row_to_config(self, row, columns, table_name):
        kwargs = {}
        kwargs["table_name"] = table_name
        for c, val in zip(columns, row):
            kwargs[c] = val

        config = TagConfig(**kwargs)
        # key is name in db
        config.key = row[0]
        return config
    
    def add_new_shape_from_row(self, row, columns, table_name):
        config:TagConfig = None
        config =  self.cvt_row_to_config(row, columns, table_name)

        bbox = list(map(int, config.coordinates.split(",")))
        r = QRect(*bbox)
        self.canvas.newShape(r, config.name, config)

    def create_db(self):
        conn = db.create_db(DATABASE_PATH)
        if conn is not None:
            cursor = conn.cursor()
            script = open("resources/static/database.sql", "r").read()
            cursor.executescript(script)
        pass

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.server.close()
        return super().closeEvent(a0)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
