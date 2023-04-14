from tools.Entities import Entity, Player
import numpy as np

class Scene:
    """ 
        Manages all logical objects in the game,
        and their interactions.
    """

    def __init__(self,renderables:dict[int,list[Entity]], camera: Player) -> None:
        """create a scene"""

        self.renderables = renderables
        self.camera = camera

    def update(self,rate : float) -> None:
        """
            Update all objects managed by the scene.

            Parameters:
                rate: framerate correction factor     
        """

        for _,objectlist in self.renderables.items():
            for object in objectlist:
                object.update(rate)
        
        self.camera.update()

    def move_camera(self,dPos:np.ndarray) -> None:
        """ Moves the camera by the given amount """

        self.camera.position += dPos

    def spin_camera(self, dEulers: np.ndarray) -> None:
        """ 
            Change the camera's euler angles by the given amount,
            performing appropriate bounds checks.
        """

        self.camera.eulers += dEulers

        if self.camera.eulers[2] < 0:
            self.camera.eulers[2] += 360
        elif self.camera.eulers[2] > 360:
            self.camera.eulers[2] -= 360
        
        self.camera.eulers[1] = min(89, max(-89, self.camera.eulers[1]))