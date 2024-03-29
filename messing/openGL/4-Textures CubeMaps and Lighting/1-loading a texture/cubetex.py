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
        self.unifNames = {None:None}

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
        if not(name in self.unifNames.keys()):
            self.unifNames[name] = glGetUniformLocation(self.shader,name)
        glUniformMatrix4fv(self.unifNames[name],1,GL_FALSE,Matrix4fv)

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

    def __init__(self) -> None:
        """create a scene"""


        self.renderables: dict[int,list[Entity]] = {}
        self.renderables[OBJECT_CUBE] = [
            Cube(
            position = [6,0,0],
            eulers = [0,0,0]
            ),
        ]

        self.camera = Player(
            position = [0,0,2],
            eulers=[0,0,0]
        )
        
    
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

################### Control ###################################################

class App:
    """ The main program """


    def __init__(self, screenWidth, screenHeight):
        """ Set up the program """

        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.set_up_glfw()

        self.make_objects()

        self.set_up_input_systems()

        self.set_up_timer()

        self.mainLoop()
    
    def set_up_glfw(self) -> None:
        """ Set up the glfw environment """

        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, 
            GLFW_CONSTANTS.GLFW_TRUE
        )
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, False)
        self.window = glfw.create_window(
            self.screenWidth, self.screenHeight, "Title", None, None
        )
        glfw.make_context_current(self.window)

    def make_objects(self) -> None:
        """ Make any object used by the App"""

        self.renderer = Renderer(
            self.screenWidth, self.screenHeight, self.window
        )
        self.scene = Scene()
    
    def set_up_input_systems(self) -> None:
        """ Run any mouse/keyboard configuration here. """

        glfw.set_input_mode(
            self.window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        )
        glfw.set_cursor_pos(
            self.window,
            self.screenWidth // 2, 
            self.screenHeight // 2
        )

        self.walk_offset_lookup = {
            1: 0,
            2: 90,
            3: 45,
            4: 180,
            6: 135,
            7: 90,
            8: 270,
            9: 315,
            11: 0,
            12: 225,
            13: 270,
            14: 180
        }
    
    def set_up_timer(self) -> None:
        """
            Set up the variables needed to measure the framerate
        """
        self.lastTime = glfw.get_time()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
    
    def mainLoop(self) -> None:
        """ Run the App """

        running = True
        while (running):

            #check events
            if glfw.window_should_close(self.window) \
                or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                running = False
            
            self.handleKeys()
            self.handleMouse()

            glfw.poll_events()

            #update scene
            self.scene.update(self.frameTime / 16.667)
            
            self.renderer.render(
                camera = self.scene.camera,
                renderables = self.scene.renderables
            )

            #timing
            self.calcuateFramerate()

        self.quit()

    def handleKeys(self) -> None:
        """
            Handle keys.
        """

        combo = 0
        directionModifier = 0

        if glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_W
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 1
        elif glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_A
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 2
        elif glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_S
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 4
        elif glfw.get_key(
            self.window, GLFW_CONSTANTS.GLFW_KEY_D
            ) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 8
        
        if combo in self.walk_offset_lookup:

            directionModifier = self.walk_offset_lookup[combo]
            
            dPos = 0.01 * np.array(
                [
                    np.cos(np.deg2rad(self.scene.camera.eulers[2] + directionModifier)),
                    np.sin(np.deg2rad(self.scene.camera.eulers[2] + directionModifier)),
                    0
                ],
                dtype = np.float32
            )

            self.scene.move_camera(dPos)

    def handleMouse(self) -> None:
        """
            Handle mouse movement.
        """

        (x,y) = glfw.get_cursor_pos(self.window)
        rate = self.frameTime / 16.667
        theta_increment = rate * ((self.screenWidth / 2.0) - x)
        phi_increment = rate * ((self.screenHeight / 2.0) - y)
        dEulers = np.array([0, phi_increment, theta_increment], dtype=np.float32)
        self.scene.spin_camera(dEulers)
        glfw.set_cursor_pos(self.window, self.screenWidth // 2, self.screenHeight // 2)

    def calcuateFramerate(self) -> None:
        """
            Calculate the framerate and frametime
        """

        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime
        if (delta >= 1):
            framerate = int(self.numFrames/delta)
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(60,framerate))
        self.numFrames += 1
    
    def quit(self):
        
        self.renderer.destroy()
        glfw.terminate()

################### View  #####################################################

class Renderer:


    def __init__(
            self,
            screenWidth: int,screenHeight: int,
            window) -> None:
        
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.set_up_opengl(window)
        self.make_assets()
        self.set_onetime_uniforms()

    def set_up_opengl(self, window) -> None:
        """
            Set up any general options used in OpenGL rendering.
        """

        glClearColor(0.0, 0.0, 0.0, 1)

        (w,h) = glfw.get_framebuffer_size(window)
        glViewport(0,0,w, h)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def make_assets(self) -> None:
        """
            Load/Create assets (eg. meshes and materials) that 
            the renderer will use.
        """

        self.meshes: dict[int, Mesh] = {
            OBJECT_CUBE: ObjMesh("models/cube.obj"),
        }

        self.materials: dict[int, Material] = {
            OBJECT_CUBE: Material("gfx/wood.jpeg"),
        }

        self.shader = Shader("shaders/vertex.txt", "shaders/fragment.txt")

    def set_onetime_uniforms(self) -> None:
        """ Set any uniforms which can simply get set once and forgotten """

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = self.screenWidth / self.screenHeight, 
            near = 0.1, far = 10, dtype = np.float32
        )

        self.shader.setMat4fv("projection",projection_transform)
        self.shader.setInt("imageTexture",0)

    def render(
            self, camera: Player, 
        renderables: dict[int, list[Entity]]) -> None:
        """
            Render a frame.
            Parameters:
                camera: the camera to render from
                renderables: a dictionary of entities to draw, keys are the
                            entity types, for each of these there is a list
                            of entities.
        """

        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader.use()

        self.shader.setMat4fv("view", camera.get_view_transform())

        for objectType,objectList in renderables.items():
            mesh = self.meshes[objectType]
            material = self.materials[objectType]
            glBindVertexArray(mesh.vao)
            material.use()
            for object in objectList:
                self.shader.setMat4fv("model",object.get_model_transform())
                glDrawArrays(GL_TRIANGLES, 0,mesh.vertex_count)
        
        glFlush()
    
    def destroy(self) -> None:
        """ Free any allocated memory """

        for (_,mesh) in self.meshes.items():
            mesh.destroy()
        for (_,material) in self.materials.items():
            material.destroy()
        self.shader.deletePgm()


class Mesh:
    """ A general mesh """


    def __init__(self):

        self.vertex_count = 0

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
    
    def destroy(self):
        
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class ObjMesh(Mesh):


    def __init__(self, filename):

        super().__init__()

        # x, y, z, s, t, nx, ny, nz
        vertices = load_model_from_file(filename)
        self.vertex_count = len(vertices)//8
        vertices = np.array(vertices, dtype=np.float32)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

class Material:

    
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        with Image.open(filepath, mode = "r") as image:
            image_width,image_height = image.size
            image = image.convert("RGBA")
            img_data = bytes(image.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

myApp = App(800,600)