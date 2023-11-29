from __future__ import annotations
from abc import abstractmethod

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application import Application

class BaseScreen:
    def __init__(self, application: Application):
        self.application = application

    @abstractmethod
    def render_static_elements(self):
        '''
        Render static elements on the screen. To be implemented by subclasses.
        '''
        pass

    @abstractmethod
    def render_dynamic_elements(self, **kwargs):
        '''
        Render dynamic elements on the screen. To be implemented by subclasses.
        '''
        pass

    @abstractmethod
    def setup(self):
        '''
        Setup the screen. To be implemented by subclasses.
        '''
        pass