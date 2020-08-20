"""Originally implemented by Andras Lasso under an MIT License


Source:
    https://github.com/Slicer/SlicerJupyter

    https://github.com/Slicer/SlicerJupyter/blob/master/JupyterNotebooks/JupyterNotebooksLib/interactive_view_widget.py

"""
from io import BytesIO
import logging

from ipycanvas import Canvas
from ipyevents import Event
from ipywidgets import Image
import numpy as np
import PIL.Image

from .constants import INTERACTION_THROTTLE, KEY_TO_SYM
from .throttler import throttle
from .utilities import screenshot


log = logging.getLogger(__name__)
log.setLevel("CRITICAL")
log.addHandler(logging.StreamHandler())


class ViewInteractiveWidget(Canvas):
    """Remote controller for VTK render windows."""

    def __init__(
        self, render_window, log_events=False, transparent_background=False, **kwargs
    ):
        """Accepts a vtkRenderWindow."""

        super().__init__(**kwargs)

        self.render_window = render_window
        self.render_window.SetOffScreenRendering(1)  # Force off screen
        self.transparent_background = transparent_background

        # Frame rate (1/renderDelay)
        self.last_render_time = 0
        self.quick_render_delay_sec = 0.1
        self.quick_render_delay_sec_range = [0.02, 2.0]
        self.adaptive_render_delay = True
        self.last_mouse_move_event = None

        # refresh if mouse is just moving (not dragging)
        self.track_mouse_move = False

        self.message_timestamp_offset = None

        self.layout.width = '100%'
        self.layout.height = 'auto'

        # Get image size
        image = self.get_image()
        # Set Canvas size
        self.width = int(image.width)
        self.height = int(image.height)
        self.draw_image(image)

        self.dragging = False

        self.interaction_events = Event()
        # Set the throttle or debounce time in millseconds (must be an non-negative integer)
        # See https://github.com/mwcraig/ipyevents/pull/55
        self.interaction_events.throttle_or_debounce = "throttle"
        self.interaction_events.wait = INTERACTION_THROTTLE
        self.interaction_events.source = self
        self.interaction_events.watched_events = [
            "dragstart",
            "mouseenter",
            "mouseleave",
            "mousedown",
            "mouseup",
            "mousemove",
            # 'wheel',  # commented out so that user can scroll through the notebook using mousewheel
            "keyup",
            "keydown",
            "contextmenu",  # prevent context menu from appearing on right-click
        ]
        # self.interaction_events.msg_throttle = 1  # does not seem to have effect
        self.interaction_events.prevent_default_action = True
        self.interaction_events.on_dom_event(self.handle_interaction_event)

        # Errors are not displayed when a widget is displayed,
        # this variable can be used to retrieve error messages
        self.error = None

        # Enable logging of UI events
        self.log_events = log_events
        self.logged_events = []
        self.elapsed_times = []
        self.age_of_processed_messages = []

    @property
    def interactor(self):
        return self.render_window.GetInteractor()

    def set_quick_render_delay(self, delay_sec):
        if delay_sec < self.quick_render_delay_sec_range[0]:
            delay_sec = self.quick_render_delay_sec_range[0]
        elif delay_sec > self.quick_render_delay_sec_range[1]:
            delay_sec = self.quick_render_delay_sec_range[1]
        self.quick_render_delay_sec = delay_sec

    def get_image(self, force_render=True):
        if force_render:
            self.render_window.Render()
        raw_img = np.uint8(
            screenshot(
                self.render_window, transparent_background=self.transparent_background
            )
        )
        f = BytesIO()
        img = PIL.Image.fromarray(raw_img)
        img.save(f, "JPEG")
        return Image(
            value=f.getvalue(), width=raw_img.shape[1], height=raw_img.shape[0]
        )

    @throttle(0.1)
    def full_render(self):
        try:
            import time

            self.draw_image(self.get_image(force_render=True))
            self.last_render_time = time.time()
        except Exception as e:
            self.error = str(e)

    def send_pending_mouse_move_event(self):
        if self.last_mouse_move_event is not None:
            self.update_interactor_event_data(self.last_mouse_move_event)
            self.interactor.MouseMoveEvent()
            self.last_mouse_move_event = None

    @throttle(0.1)
    def quick_render(self):
        try:
            import time

            self.send_pending_mouse_move_event()
            self.draw_image(self.get_image(force_render=False))
            if self.log_events:
                self.elapsed_times.append(time.time() - self.last_render_time)
            self.last_render_time = time.time()
        except Exception as e:
            self.error = str(e)

    def update_interactor_event_data(self, event):
        try:
            if event["event"] == "keydown" or event["event"] == "keyup":
                key = event["key"]
                sym = KEY_TO_SYM[key] if key in KEY_TO_SYM.keys() else key
                self.interactor.SetKeySym(sym)
                if len(key) == 1:
                    self.interactor.SetKeyCode(key)
                self.interactor.SetRepeatCount(1)
            else:
                self.interactor.SetEventPosition(
                    event["offsetX"], self.height - event["offsetY"]
                )
            self.interactor.SetShiftKey(event["shiftKey"])
            self.interactor.SetControlKey(event["ctrlKey"])
            self.interactor.SetAltKey(event["altKey"])
        except Exception as e:
            self.error = str(e)

    def handle_interaction_event(self, event):
        try:
            if self.log_events:
                self.logged_events.append(event)
            if event["event"] == "mousemove":
                import time

                if self.message_timestamp_offset is None:
                    self.message_timestamp_offset = (
                        time.time() - event["timeStamp"] * 0.001
                    )
                self.last_mouse_move_event = event
                if not self.dragging and not self.track_mouse_move:
                    return
                if self.adaptive_render_delay:
                    ageOfProcessedMessage = time.time() - (
                        event["timeStamp"] * 0.001 + self.message_timestamp_offset
                    )
                    if ageOfProcessedMessage > 1.5 * self.quick_render_delay_sec:
                        # we are falling behind, try to render less frequently
                        self.set_quick_render_delay(self.quick_render_delay_sec * 1.05)
                    elif ageOfProcessedMessage < 0.5 * self.quick_render_delay_sec:
                        # we can keep up with events, try to render more frequently
                        self.set_quick_render_delay(self.quick_render_delay_sec / 1.05)
                    if self.log_events:
                        self.age_of_processed_messages.append(
                            [ageOfProcessedMessage, self.quick_render_delay_sec]
                        )
                # We need to render something now it no rendering since self.quick_render_delay_sec
                if time.time() - self.last_render_time > self.quick_render_delay_sec:
                    self.quick_render()
            elif event["event"] == "mouseenter":
                self.update_interactor_event_data(event)
                self.interactor.EnterEvent()
                self.last_mouse_move_event = None
            elif event["event"] == "mouseleave":
                self.update_interactor_event_data(event)
                self.interactor.LeaveEvent()
                self.last_mouse_move_event = None
            elif event["event"] == "mousedown":
                self.dragging = True
                self.send_pending_mouse_move_event()
                self.update_interactor_event_data(event)
                if event["button"] == 0:
                    self.interactor.LeftButtonPressEvent()
                elif event["button"] == 2:
                    self.interactor.RightButtonPressEvent()
                elif event["button"] == 1:
                    self.interactor.MiddleButtonPressEvent()
                self.full_render()
            elif event["event"] == "mouseup":
                self.send_pending_mouse_move_event()
                self.update_interactor_event_data(event)
                if event["button"] == 0:
                    self.interactor.LeftButtonReleaseEvent()
                elif event["button"] == 2:
                    self.interactor.RightButtonReleaseEvent()
                elif event["button"] == 1:
                    self.interactor.MiddleButtonReleaseEvent()
                self.dragging = False
                self.full_render()
            elif event["event"] == "keydown":
                self.send_pending_mouse_move_event()
                self.update_interactor_event_data(event)
                self.interactor.KeyPressEvent()
                self.interactor.CharEvent()
                if (
                    event["key"] != "Shift"
                    and event["key"] != "Control"
                    and event["key"] != "Alt"
                ):
                    self.full_render()
            elif event["event"] == "keyup":
                self.send_pending_mouse_move_event()
                self.update_interactor_event_data(event)
                self.interactor.KeyReleaseEvent()
                if (
                    event["key"] != "Shift"
                    and event["key"] != "Control"
                    and event["key"] != "Alt"
                ):
                    self.full_render()
        except Exception as e:
            self.error = str(e)
