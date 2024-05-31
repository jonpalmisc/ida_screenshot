import ida_idaapi
import ida_kernwin

from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtGui import QPixmap, QRegion
from PyQt5.QtWidgets import QApplication, QWidget


def scale_size(r: QRect, scale: int) -> QSize:
    s = QRect(r)

    s.setWidth(r.width() * scale)
    s.setHeight(r.height() * scale)

    return s.size()


def render_widget_img(widget: QWidget, scale: int) -> QPixmap:
    rect = widget.rect()

    img = QPixmap(scale_size(rect, scale))
    img.setDevicePixelRatio(scale)
    widget.render(img, QPoint(), QRegion(rect))

    return img


class screenshot_handler_t(ida_kernwin.action_handler_t):
    widget_only: bool
    save_to_file: bool

    def __init__(self, widget_only: bool, save_to_file: bool):
        ida_kernwin.action_handler_t.__init__(self)
        self.widget_only = widget_only
        self.save_to_file = save_to_file

    def activate(self, ctx):  # pyright: ignore
        if self.widget_only:
            cur_twidget = ida_kernwin.get_current_widget()
            target = ida_kernwin.PluginForm.TWidgetToPyQtWidget(cur_twidget)
        else:
            target = QApplication.activeWindow()

        if target is None:
            print("Could not find widget or window!")
            return 1

        scale = ida_kernwin.ask_long(2, "Screenshot scale multiplier:")
        if not scale or scale < 1:
            scale = 1

        img = render_widget_img(target, scale)
        if self.save_to_file:
            path = ida_kernwin.ask_file(True, "screenshot.png", "Save screenshot")
            if path:
                img.save(path)
        else:
            QApplication.clipboard().setImage(img.toImage())

        return 1

    def update(self, ctx):
        return ida_kernwin.AST_ENABLE_ALWAYS


ACTION_CAPTURE_WIDGET_COPY = "screenshot:CaptureWidgetCopy"
ACTION_CAPTURE_WINDOW_COPY = "screenshot:CaptureWindowCopy"
ACTION_CAPTURE_WIDGET_SAVE = "screenshot:CaptureWidgetSave"
ACTION_CAPTURE_WINDOW_SAVE = "screenshot:CaptureWindowSave"


class screenshot_ui_hooks_t(ida_kernwin.UI_Hooks):
    popup_actions = []

    def finish_populating_widget_popup(self, widget, popup):  # pyright: ignore
        for action in [
            ACTION_CAPTURE_WIDGET_COPY,
            ACTION_CAPTURE_WINDOW_COPY,
            ACTION_CAPTURE_WIDGET_SAVE,
            ACTION_CAPTURE_WINDOW_SAVE,
        ]:
            ida_kernwin.attach_action_to_popup(
                widget,
                popup,
                action,
                f"Sc&reenshot/",
                ida_kernwin.SETMENU_APP,
            )


class screenshot_plugin_t(ida_idaapi.plugin_t):
    flags = ida_idaapi.PLUGIN_DRAW | ida_idaapi.PLUGIN_HIDE
    help = ""
    comment = "Screenshot Capture"
    wanted_name = "screenshot"
    wanted_hotkey = ""

    ui_hooks: screenshot_ui_hooks_t

    def init(self):
        self.ui_hooks = screenshot_ui_hooks_t()

        ida_kernwin.register_action(
            ida_kernwin.action_desc_t(
                ACTION_CAPTURE_WIDGET_COPY,
                "Copy wid~g~et screenshot to clipboard",
                screenshot_handler_t(True, False),
                None,
                "Copy a screenshot of the current widget to the clipboard",
            )
        )
        ida_kernwin.register_action(
            ida_kernwin.action_desc_t(
                ACTION_CAPTURE_WINDOW_COPY,
                "Copy ~w~indow screenshot to clipboard",
                screenshot_handler_t(False, False),
                None,
                "Copy a screenshot of the current window to the clipboard",
            )
        )
        ida_kernwin.register_action(
            ida_kernwin.action_desc_t(
                ACTION_CAPTURE_WIDGET_SAVE,
                "Save widget screenshot to file...",
                screenshot_handler_t(True, True),
                None,
                "Save a screenshot of the current widget to a file",
            )
        )
        ida_kernwin.register_action(
            ida_kernwin.action_desc_t(
                ACTION_CAPTURE_WINDOW_SAVE,
                "Save window screenshot to file...",
                screenshot_handler_t(False, True),
                None,
                "Save a screenshot of the current window to a file",
            )
        )

        self.ui_hooks.hook()
        return ida_idaapi.PLUGIN_KEEP

    def run(self):  # pyright: ignore
        pass

    def term(self):
        self.ui_hooks.unhook()


def PLUGIN_ENTRY():
    return screenshot_plugin_t()
