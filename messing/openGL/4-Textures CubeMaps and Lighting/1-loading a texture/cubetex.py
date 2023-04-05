import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from PIL import Image

################### Constants        ########################################

OBJECT_CUBE = 0
OBJECT_CAMERA = 1


################### Helper Functions ########################################

class Shader():
    """
        COmpile and use Shader
    """

    def __init__(self, vertexPath:str, fragmentPath:str):
        self.createShader(vertexPath,fragmentPath)

    def createShader(self,vertexPath:str, fragmentPath:str):

        with open(vertexPath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentPath,'r') as f:
            fragment_src = f.readlines()
        
        self.shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                                     compileShader(fragment_src,GL_FRAGMENT_SHADER))
        
    def use(self) -> None:
        glUseProgram(self.shader)

    def setBool(self, name:str, value:bool) -> None:
        self.use()
        glUniform1i(glGetUniformLocation(self.shader,name), int(value))

    def setInt(self, name:str, value:int) -> None:
        self.use()
        glUniform1i(glGetUniformLocation(self.shader,name), value)

    def setFloat(self, name:str, value:np.float32) -> None:
        self.use()
        glUniform1f(glGetUniformLocation(self.shader,name), value)
    
    def setVec2f(self,name:str, value) -> None:
        self.use()
        glUniform2f(glGetUniformLocation(self.shader,name), value[0], value[1])

    def setMat4fv(self, name:str, Matrix4fv:pyrr.matrix44) -> None:
        self.use()
        glUniformMatrix4fv(glGetUniformLocation(self.shader,name),Matrix4fv)

    def deletePgm(self):
        glDeleteProgram(self.shader)


def load_model_from_file(filename:str) -> list[float]:
    """ 
        Read the given obj file and return a list of all the
        vertex data.
    """

    v=[]
    vt=[]
    vn=[]
    vertices=[]

    with open(filename,'r') as f:
        line = f.readline()
        while line:
            words = line.split(' ')
            if words[0]=='v':
                v.append(read_vertex_data(words))
            elif words[0]=='vt':
                vt.append(read_texcoord_data(words))
            elif words[0]=='vn':
                vn.append(read_normal_data(words))
            elif words[0]=='f':
                read_face_data(words,v,vt,vn,vertices)
            line=f.readline()
    
    return vertices

def read_vertex_data(words:list[str])->list[float]:
    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]

def read_texcoord_data(words:list[str])->list[float]:
    return [
        float(words[1]),
        float(words[2])
    ]

def read_normal_data(words:list[str])->list[float]:
    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]

def read_face_data(words:list[str], 
                   v:list[float],
                   vt:list[float],
                   vn:list[float],
                   vertices:list[float]) -> list[float]:
    
    """
        Read the given face description, and use the
        data from the pre-filled v, vt, vn arrays to add
        data to the vertices array
    """

    triangles_in_face = len(words)-3

    for i in range(triangles_in_face):
        read_corner(words[1],v,vt,vn,vertices)
        read_corner(words[i+2],v,vt,vn,vertices)
        read_corner(words[i+3],v,vt,vn,vertices)

def read_corner(description: str, 
    v: list[float], vt: list[float], vn: list[float], 
    vertices: list[float]) -> None:
    """
        Read the given corner description, then send the
        approprate v, vt, vn data to the vertices array.
    """

    v_vt_vn = description.split('/')

    for x in v[int(v_vt_vn[0])-1]:
        vertices.append(x)
    for x in vt[int(v_vt_vn[1])-1]:
        vertices.append(x)
    for x in vn[int(v_vt_vn[2])-1]:
        vertices.append(x)


################### Model #####################################################

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
    def __init__(self,position:list[float],eulers:list[float]) -> None:
        super().__init__(position,eulers,OBJECT_CUBE)

    def update(self,rate:float) -> None:
        self.eulers[2] += 0.25 * rate
        if self.eulers[2] > 360:
            self.eulers[2] -= 360

class Player(Entity):
    """ A first person camera controller. """

    def __init__(self, position: list[float], eulers: list[float]) -> None:
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
    

class Scene:
    """ 
        Manages all logical objects in the game,
        and their interactions.
    """