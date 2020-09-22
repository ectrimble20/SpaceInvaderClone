"""
Event handling module, wraps many of the build in pygame.event methods but does not expose them
"""
from pygame.event import Event, get, post, custom_type


__all__ = ['bind_listener', 'unbind_listener', 'clear_listeners', 'post_event', 'process_queue', 'build_event',
           'register_new_type']


_listeners = {}


def bind_listener(listener: callable, event_type: int) -> None:
    """
    Bind a listener function to an event type
    :param listener: callable
    :param event_type: int
    :return: None
    """
    if event_type not in _listeners.keys():
        _listeners[event_type] = []
    _listeners[event_type].append(listener)


def unbind_listener(listener: callable, event_type: int) -> None:
    """
    Unbind a listener function from an event type
    Note: prints warnings if an invalid event type or a non-existent listener is passed
    :param listener: callable
    :param event_type: int
    :return: None
    """
    if event_type not in _listeners.keys():
        print(f"Warning: event_type {event_type} not present in listener binds")
        return None
    if listener not in _listeners[event_type]:
        print(f"Warning: listener {listener} not present in listener binds")
        return None
    _listeners[event_type].remove(listener)


def clear_listeners() -> None:
    """
    Clears the listener binds, useful when switching out of a scene that simply needs to not respond to events anymore
    :return: None
    """
    _listeners.clear()


def post_event(event: Event) -> None:
    """
    Post an event into the PyGame event queue (SDL process)
    :param event: Event
    :return: None
    """
    post(event)


def process_queue() -> None:
    """
    Processes the PyGame event queue and hands off events to any listeners registered to handle them
    :return: None
    """
    for event in get():
        if event.type in _listeners.keys():
            for listener in _listeners[event.type]:
                listener(event)


def build_event(event_type_id: int, **kwargs) -> Event:
    """
    Pass-through function to build a PyGame event
    :param event_type_id: int
    :param kwargs: mixed, key-value data passed to the event
    :return: Event
    """
    return Event(event_type_id, **kwargs)


def register_new_type() -> int:
    """
    Calls the custom_type function from the PyGame event module to create a new user type, effectively registering a new
    event type ID that can be used.
    :return: int
    """
    return custom_type()
