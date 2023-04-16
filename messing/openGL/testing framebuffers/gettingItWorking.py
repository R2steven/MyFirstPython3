import sys
sys.path.insert(0,'..')
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from tools.Entities import Entity,Player,Square,Cube
from tools.Objects import Mesh,ObjMesh,Material
from tools.Shader import Shader as sdr
from tools.Setup import AppSetup
from tools.Scene import Scene
import numpy as np
import pyrr


"""
    Usage:
        Stage(Scene): sets and handles all of the entities and positions
            IMPLEMENT: create or feed list of renderables of form
                        dict[int,list[Entity]]
        
        App(AppSetup): runs main game logic loop and inputs/actions
            IMPLEMENT:
                make_objects: takes implementation of renderer and Stage(Scene)
                mainLoop: handles game loop
        
        Renderer: runs opengl render loop
            Implement: setup opengl, load meshes, 
                        set onetime uniforms, render objs
"""

################### Constants        ########################################

OBJECT_SQUARE = 0
OBJECT_CUBE = 1
OBJECT_CAMERA = 2
SQUARE_pth = "models/square.obj"
CUBE_pth = "models/cube.obj"
CUBE_txt_pth = "gfx/wood.jpeg"
SCREEN_pth = "models/screen.obj"
scn_sdr_vtx_pth = "shaders/vertex.txt"
scn_sdr_frg_pth = "shaders/fragment.txt"
scrn_sdr_vtx_pth = "shaders/screenVertex.txt"
scrn_sdr_frg_pth = "shaders/screenFragment.txt"

Screen_Width = 800
Screen_Height = 600


################### Model #####################################################

class Stage(Scene):
    """ 
        Manages all logical objects in the game,
        and their interactions.
    """

    def __init__(self) -> None:
        """create a scene"""


        self.renderables: dict[int,list[Entity]] = {}
        self.renderables[OBJECT_SQUARE] = [
            Square(
            position = [6,0,2],
            eulers = [0,0,0],
            OBJECT_SQUARE=OBJECT_SQUARE
            ),
        ]

        self.renderables[OBJECT_CUBE] = [
            Cube(
            position=[0,6,2],
            eulers= [0,0,0],
            OBJECT_CUBE=OBJECT_CUBE
            )
        ]

        self.camera = Player(
            position = [0,0,2],
            eulers=[0,0,0],
            OBJECT_CAMERA=OBJECT_CAMERA
        )

################### Control ###################################################

class App(AppSetup):
    """ The main program """


    def __init__(self, screenWidth, screenHeight):
        """ Set up the program """
        super().__init__(screenWidth,screenHeight)


        
    def make_objects(self) -> None:
        """ Make any object used by the App"""

        self.renderer = Renderer(
            self.screenWidth, self.screenHeight, self.window
        )
        self.scene = Stage()
    
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
            self.scene.update(0)
            
            self.renderer.render(
                camera = self.scene.camera,
                renderables = self.scene.renderables
            )

            #timing
            self.calcuateFramerate()

        self.quit()

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
            OBJECT_SQUARE: ObjMesh(SQUARE_pth),
        }

        self.materials: dict[int, Material] = {
            OBJECT_SQUARE: Material(CUBE_txt_pth),
        }

        self.meshes[OBJECT_CUBE] = ObjMesh(CUBE_pth)
             
        self.materials[OBJECT_CUBE] = Material(CUBE_txt_pth)

        self.screenobj = ObjMesh(SCREEN_pth)

        self.SCENEshader = sdr(scn_sdr_vtx_pth, scn_sdr_frg_pth)
        self.SCREENshader = sdr(scrn_sdr_vtx_pth,scrn_sdr_frg_pth)
        self.fbo = frameBuffer()

    def set_onetime_uniforms(self) -> None:
        """ Set any uniforms which can simply get set once and forgotten """

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = self.screenWidth / self.screenHeight, 
            near = 0.1, far = 100, dtype = np.float32
        )

        self.SCENEshader.setMat4fv("projection",projection_transform)
        self.SCENEshader.setInt("imageTexture",0)

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
        self.fbo.use()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.SCENEshader.use()

        self.SCENEshader.setMat4fv("view", camera.get_view_transform())

        for objectType,objectList in renderables.items():
            mesh = self.meshes[objectType]
            material = self.materials[objectType]
            glBindVertexArray(mesh.vao)
            material.use()
            for object in objectList:
                self.SCENEshader.setMat4fv("model",object.get_model_transform())
                glDrawArrays(GL_TRIANGLES, 0,mesh.vertex_count)

        glBindFramebuffer(GL_FRAMEBUFFER,0)
        glDisable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT)
        self.SCREENshader.use()
        
        glBindVertexArray(self.screenobj.vao)
        glBindTexture(GL_TEXTURE_2D,self.fbo.texture)
        glDrawArrays(GL_TRIANGLES, 0,self.screenobj.vertex_count)
        
        glFlush()
    
    def destroy(self) -> None:
        """ Free any allocated memory """

        for (_,mesh) in self.meshes.items():
            mesh.destroy()
        for (_,material) in self.materials.items():
            material.destroy()
        self.SCENEshader.deletePgm()

############### Framebuffers ##################################################
class frameBuffer:
    
    def __init__(self):
        self.Create_framebuffer()

    def Create_framebuffer(self):

        self.FBufferObj = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER,self.FBufferObj)
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,Screen_Width,Screen_Height,0,GL_RGBA,GL_UNSIGNED_BYTE,None)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,self.texture,0)

        self.renderbuff = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER,self.renderbuff)
        glRenderbufferStorage(GL_RENDERBUFFER,GL_DEPTH24_STENCIL8,Screen_Width,Screen_Height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_DEPTH_STENCIL_ATTACHMENT,GL_RENDERBUFFER,self.renderbuff)

    def use(self):
        glBindFramebuffer(GL_FRAMEBUFFER,self.FBufferObj)
        glClearColor(0.1,0.1,0.1,0.1)
        glEnable(GL_DEPTH_TEST)
        

    def delete(self):
        glDeleteFramebuffers(1,(self.FBufferObj,))







myApp = App(Screen_Width,Screen_Height)