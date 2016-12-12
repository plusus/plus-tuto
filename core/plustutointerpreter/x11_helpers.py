import time

from ewmh import EWMH
from Xlib.display import Display
from Xlib import Xatom, protocol, X, Xutil
from Xlib.xobject.drawable import Window


CACHED_EWMH = None
""":type: EWMH"""


def get_cached_ewmh(display):
    global CACHED_EWMH
    if CACHED_EWMH is not None and CACHED_EWMH.display is display:
        ewmh = CACHED_EWMH
    else:
        ewmh = CACHED_EWMH = EWMH(display)
    return ewmh


def get_x_clients(display):
    """
    Get all visible window IDs
    :type display: Display
    :return: List of visible window ids
    :rtype: List[int]
    """
    root_window = display.screen().root
    return [x for x in root_window.get_full_property(
            display.intern_atom('_NET_CLIENT_LIST'), Xatom.WINDOW).value]


def poll_new_x_client(window_name,
                      interval_seconds=0.1,
                      timeout_seconds=10,
                      win_id_exclusion=None):
    """
    Waits for an application containing window_name and returns its id.
    :type window_name: str
    :param interval_seconds: The interval at which we search for new windows
    :type interval_seconds: float
    :type timeout_seconds: float
    :type win_id_exclusion: int
    :return: The id of the most recent window containing window_name
    :rtype int
    """

    display = Display()
    initial_clients = get_x_clients(display)
    new_x_client = None

    # Calls get_x_clients many times to know if a new window has appeared
    for _ in range(int(timeout_seconds//interval_seconds)):
        client = get_window_from_string(display, window_name)

        if client is not None and client not in initial_clients\
                and client is not win_id_exclusion:
            new_x_client = client
            break
        time.sleep(interval_seconds)

    return new_x_client


def get_window_from_string(display, substring):
    """
    :type display: Display
    :type substring: str
    :return: The id of the window containing the substring
    :rtype: int
    """
    for client in get_x_clients(display):
        wm_name = str(get_window_object_from_id(display, client).get_wm_name())
        if substring in wm_name:
            return client
    return None


def get_window_from_process_name(display, command):
    """
    :type display: Display
    :type command: str
    :return: The id of the window run by the command
    :rtype: int
    """
    for client in get_x_clients(display):
        wm_class = str(get_window_object_from_id(display, client).get_wm_class()[0])
        if wm_class in command:
            return client
    return None


def get_window_object_from_id(display, windowId):
    """
    :type display: Display
    :type windowId: int
    :rtype: Window
    """
    return display.create_resource_object('window', windowId)


def get_atom(display, atom):
    """
    :type display: Display
    :type atom: str
    :rtype: int
    """
    return display.intern_atom(atom)


def send_client_message(display, window, message):
    """
    :type display: Display
    :type window: Window
    :type message: str
    """
    event_type = get_atom(display, message)
    mask = X.SubstructureRedirectMask
    data = [0, 0, 0, 0, 0]
    event = protocol.event.ClientMessage(
        window=window,
        client_type=event_type,
        data=(32, data))
    display.screen().root.send_event(event, mask)
    display.sync()


def close_window(display, window):
    """
    :type display: Display
    :type window: Window
    """
    send_client_message(display, window, '_NET_CLOSE_WINDOW')


def raise_window(display, window):
    """
    :type display: Display
    :type window: Window
    """
    send_client_message(display, window, '_NET_ACTIVE_WINDOW')


def send_mouse_event(display, window, x, y):
    """
    :type display: Display
    :type window: Window
    :type x: int
    :type y: int
    """
    root = display.screen().root
    root_click_position = root.translate_coords(window, x, y)
    mouse_press = protocol.event.ButtonPress(
        time=X.CurrentTime,
        root=root,
        window=window,
        same_screen=1,
        child=X.NONE,
        root_x=root_click_position.x,
        root_y=root_click_position.y,
        event_x=x,
        event_y=y,
        state=0,
        detail=1  # first button
    )
    window.send_event(mouse_press)
    display.sync()

    mouse_release = protocol.event.ButtonRelease(
        time=X.CurrentTime,
        root=root,
        window=window,
        same_screen=1,
        child=X.NONE,
        root_x=root_click_position.x,
        root_y=root_click_position.y,
        event_x=x,
        event_y=y,
        state=0,
        detail=1  # first button
    )
    window.send_event(mouse_release)
    display.sync()


def minimize_window(display, window):
    """
    :type display: Display
    :type window: Window
    """
    change_state(display, window, Xutil.IconicState)


def unmaximize_window(display, window):
    """
    :type display: Display
    :type window: Window
    """
    emwh = get_cached_ewmh(display)
    emwh.setWmState(window, 0, "_NET_WM_STATE_MAXIMIZED_VERT")
    emwh.setWmState(window, 0, "_NET_WM_STATE_MAXIMIZED_HORZ")


def set_normal_state(display, window):
    """
    :type display: Display
    :type window: Window
    """
    change_state(display, window, Xutil.NormalState)


def change_state(display, window, state):
    """
    :type display: Display
    :type window: Window
    :type state: int
    """
    event_type = get_atom(display, 'WM_CHANGE_STATE')
    mask = X.SubstructureRedirectMask
    data = [state, 0, 0, 0, 0]
    event = protocol.event.ClientMessage(
        window=window,
        client_type=event_type,
        data=(32, data))
    display.screen().root.send_event(event, mask)
    display.sync()


def get_top_parent(display, window):
    """
    :type display: Display
    :type window: Window
    :rtype: Window
    """
    top_clients = display.screen().root.query_tree().children
    for top_client in top_clients:
        if top_client == window or is_child_recursive(top_client, window):
            return top_client


def is_child_recursive(window, possible_child):
    """
    :type window: Window
    :type possible_child: Window
    :rtype: bool
    """
    children = window.query_tree().children
    for child in children:
        if child == possible_child:
            return True
        else:
            return is_child_recursive(child, possible_child)
    return False


def get_stacking_index(display, window):
    """
    :type display: Display
    :type window: Window
    :rtype: int
    """
    try:
        index = display.screen().root.query_tree().children.index(window)
    except ValueError or RuntimeError:
        index = None
    return index
