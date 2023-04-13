import numpy as np
import pyrr

"""
    Make and handle entities such as cameras, players, cubes, etc    
"""

class Entity:
    """ Represents a general object with a position and rotation applied"""

    def __init__(self,
                 position:list[float],
                 eulers:list[float],
                 objectType:int) -> None:
        
        """
            Initialize the entity, store its state and update its transform.
            Parameters:
                position: The position of the entity in the world (x,y,z)
                eulers: Angles (in degrees) representing rotations around the x,y,z axes.
                objectType: The type of object which the entity represents,
                            this should match a named constant.
        """
        self.position = np.array(position,dtype=np.float32)
        self.eulers = np.array(eulers,dtype=np.float32)
        self.objectType = objectType

    def get_model_transform(self) ->np.ndarray:
        """
            Calculates and returns the entity's transform matrix,
            based on its position and rotation.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform,
            m2=pyrr.matrix44.create_from_z_rotation(
            theta=np.radians(self.eulers[2]),
            dtype=np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=self.position,
                dtype=np.float32
            )
        )

        return model_transform
    
    def update(self, rate: float) -> None:
        raise NotImplementedError

    
class Cube(Entity):
    def __init__(self,position:list[float],eulers:list[float],OBJECT_CUBE) -> None:
        super().__init__(position,eulers,OBJECT_CUBE)

    def update(self,rate:float) -> None:
        self.eulers[2] += 0.25 * rate
        if self.eulers[2] > 360:
            self.eulers[2] -= 360

class Player(Entity):
    """ A first person camera controller. """

    def __init__(self, position: list[float], eulers: list[float],OBJECT_CAMERA) -> None:
        super().__init__(position, eulers, OBJECT_CAMERA)

        self.localUp = np.array([0,0,1],dtype=np.float32)

        #directions after rotation
        self.up = np.array([0,0,1],dtype=np.float32)
        self.right = np.array([0,1,0],dtype=np.float32)
        self.forwards = np.array([1,0,0],dtype=np.float32)

    def calculate_vectors(self) -> None:

        """ 
            Calculate the camera's fundamental vectors.
            There are various ways to do this, this function
            achieves it by using cross products to produce
            an orthonormal basis.
        """
        #calculate the forwards vector directly using spherical coordinates
        self.forwards = np.array(
            [
            np.cos(np.radians(self.eulers[2]))*np.cos(np.radians(self.eulers[1])),
            np.sin(np.radians(self.eulers[2]))*np.cos(np.radians(self.eulers[1])),
            np.sin(np.radians(self.eulers[1]))
            ],
            dtype=np.float32
        )

        self.right = pyrr.vector.normalise(np.cross(self.forwards,self.localUp))
        self.up = pyrr.vector.normalise(np.cross(self.right,self.forwards))
        
    def update(self) -> None:
        """Updates the camera"""
        self.calculate_vectors()

    def get_view_transform(self) -> np.ndarray:
        return pyrr.matrix44.create_look_at(
            eye = self.position,
            target=self.position + self.forwards,
            up = self.up,
            dtype= np.float32
        )