
from ui.config_ui import Ui_ConfigDlg
from ui.font_ui import Ui_FontDlg
from ui.shortcut_ui import Ui_ShortcutDlg
from libs.shape import Shape
from libs.tag_config import TagConfig
from libs.utils import *
from libs.constant import *

class ShortcutDlg(QDialog):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.ui = Ui_ShortcutDlg()
        self.ui.setupUi(self)

class ListShapeDlg(QListWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("font:bold 12px")

    def change_item_shape(self, index:int=None, text:str=None, color:QColor=None):
        if text is not None and index is not None:
            self.item(index).setText(text)
        if color is not None and index is not None:
            self.item(index).setBackground(color)

    def add_item_shape(self, s:Shape):
        it = QListWidgetItem(s.label)
        it.setBackground(s.color)
        it.setForeground(Qt.white)
        self.addItem(it)

    def remove_item_shape(self, index):
        self.takeItem(index)
        

class ConfigDlg(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.ui = Ui_ConfigDlg()
        self.ui.setupUi(self)

        self.ui.groupBox.setLayout(self.ui.formLayout)

        self.applyAction = newAction(self, "Apply", shortcut="ctrl+d", icon="apply")
        btn_apply = newToolButton(self.applyAction, self)

        self.saveAction = newAction(self, "Save", shortcut="ctrl+s", icon="save")
        btn_save = newToolButton(self.saveAction, self)

        btn_apply.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        btn_save.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        addWidgets(layout, [self.ui.groupBox, new_hlayout([btn_apply, btn_save])], [5, 1])
        
        self.ui.cbb_tags.setCurrentIndex(-1)
        self.ui.ln_coordinates.setEnabled(False)
        self.ui.cbb_tags.currentIndexChanged.connect(self.tag_selected)
        self.set_editable(False)

        self._ln_show = []
        self._ln_hide = []

    def set_editable(self, b:bool):
        self.ui.groupBox.setEnabled(b)
        self.applyAction.setEnabled(b)
        self.saveAction.setEnabled(b)


    def tag_selected(self):
        tag_name = self.ui.cbb_tags.currentText().lower()
        if not tag_name:
            return

        ln_all = self.ui.groupBox.children()
        ln_all = [a for a in ln_all if isinstance(a, QLineEdit)]
        
        if tag_name == TRANSFER_TABLE:
            ln_hide = [self.ui.ln_speed, self.ui.ln_state, self.ui.ln_type]

        elif tag_name == TURN_TABLE:
            ln_hide = [self.ui.ln_speed, self.ui.ln_state]

        elif tag_name == ELEVATOR_TABLE:
            ln_hide = [self.ui.ln_speed, self.ui.ln_dir, self.ui.ln_type, self.ui.ln_gr_tag]

        elif tag_name == STANDBY_TABLE:
            ln_hide = [self.ui.ln_speed, self.ui.ln_state, self.ui.ln_dir, self.ui.ln_type, self.ui.ln_gr_tag]

        elif tag_name == SPEED_TABLE:
            ln_hide = [self.ui.ln_state, self.ui.ln_dir, self.ui.ln_type, self.ui.ln_gr_tag]

        elif tag_name == DISPLAY_TABLE:
            ln_hide = [self.ui.ln_speed, self.ui.ln_state, self.ui.ln_dir, self.ui.ln_type, self.ui.ln_gr_tag]

        elif tag_name == OTHER_TABLE:
            ln_hide = [self.ui.ln_speed, self.ui.ln_state, self.ui.ln_dir, self.ui.ln_gr_tag]


        self._ln_hide = ln_hide
        self._ln_show = [ln for ln in ln_all if ln not in ln_hide]

        for ln in self._ln_show:
            ln.setStyleSheet("background:yellow")
            ln.setEnabled(True)

        for ln in self._ln_hide:
            ln.setStyleSheet("")
            ln.setEnabled(False)

    def current_tag(self):
        return self.ui.cbb_tags.currentText()

    def set(self, config:TagConfig):
       table_name = config.table_name.upper()
       if table_name:
           self.ui.cbb_tags.setCurrentText(table_name)
       else:
           self.ui.cbb_tags.setCurrentIndex(-1)

       self.ui.ln_name.setText(config.name)
       self.ui.ln_x.setText(config.x)
       self.ui.ln_y.setText(config.y)
       self.ui.ln_rfid.setText(config.rfid)
       self.ui.ln_dir.setText(config.dir)
       self.ui.ln_gr_tag.setText(config.group_tag)
       self.ui.ln_type.setText(config.type)
       self.ui.ln_state.setText(config.state)
       self.ui.ln_speed.setText(config.speed)
       self.ui.ln_coordinates.setText(config.coordinates)

    
    def get(self) -> dict:
        config = {}
        config["table_name"] = self.ui.cbb_tags.currentText().lower()
        config["name"] = self.ui.ln_name.text()
        config["x"] = self.ui.ln_x.text()
        config["y"] = self.ui.ln_y.text()
        config["rfid"] = self.ui.ln_rfid.text()

        if self.ui.ln_dir.isEnabled():
            config["dir"] = self.ui.ln_dir.text()

        if self.ui.ln_type.isEnabled():
            config["type"] = self.ui.ln_type.text()

        if self.ui.ln_gr_tag.isEnabled():
            config["group_tag"] = self.ui.ln_gr_tag.text()

        if self.ui.ln_state.isEnabled():
            config["state"] = self.ui.ln_state.text()

        if self.ui.ln_speed.isEnabled():
            config["speed"] = self.ui.ln_speed.text()

        config["coordinates"] = self.ui.ln_coordinates.text()

        return config
            

class FontDlg(QDialog):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.ui = Ui_FontDlg()
        self.ui.setupUi(self)

        bb = newBB(self)

        self.ui.formLayout.addRow("", bb)
        self.setLayout(self.ui.formLayout)

        self.ui.btn_color_transfer.clicked.connect(lambda:self.on_clicked_choose_color("transfer"))
        self.ui.btn_color_turn.clicked.connect(lambda:self.on_clicked_choose_color("turn"))
        self.ui.btn_color_elevator.clicked.connect(lambda:self.on_clicked_choose_color("elevator"))
        self.ui.btn_color_speed.clicked.connect(lambda:self.on_clicked_choose_color("speed"))
        self.ui.btn_color_standby.clicked.connect(lambda:self.on_clicked_choose_color("standby"))
        self.ui.btn_color_display.clicked.connect(lambda:self.on_clicked_choose_color("display"))
        self.ui.btn_color_other.clicked.connect(lambda:self.on_clicked_choose_color("other"))

        self._colors = {}

    def on_clicked_choose_color(self, table_name=""):
        dlg = QColorDialog(Qt.black, self)
        if dlg.exec_():
            qcolor:QColor = dlg.selectedColor()
            qcolor.setAlpha(175)
            hex_color = qcolor.name()
            self.sender().setStyleSheet("border:None;background:%s" % hex_color)
            self._colors[table_name] = hex_color

    def get(self):
        font = {
            "thickness": self.ui.sp_thickness.value(),
            "fontsize": self.ui.sp_fontsize.value(),
            "radius": self.ui.sp_radius.value()
        }
        for key in self._colors:
            font[key] = self._colors[key]
        return font

    def set(self, font):
        self.ui.sp_thickness.setValue(font.get("thickness", 1))
        self.ui.sp_fontsize.setValue(font.get("fontsize", 10))
        self.ui.sp_radius.setValue(font.get("radius", 5))

        keys = ["transfer", "turn", "elevator", "standby", "display", "speed", "other"]
        buttons = [self.ui.btn_color_transfer, self.ui.btn_color_turn, self.ui.btn_color_elevator,
                   self.ui.btn_color_standby, self.ui.btn_color_display, self.ui.btn_color_speed, self.ui.btn_color_other]

        for key, btn in zip(keys, buttons):
            hex_color = font.get(key, None)
            if hex_color:
                self._colors[key] = hex_color
                btn.setStyleSheet("border:None;background:%s" % hex_color)
        
    def popup(self, font={}):
        self.set(font)
        return self.get() if self.exec_() else None
