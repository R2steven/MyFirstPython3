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

## TODO: render needs shader compiled, refresh screen, destroy shader
        ## need to set up compute, compute shader, screen shader, fragment shader

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

compute_sdr_pth = "shaders/compute.txt"
vertex_sdr_pth = "shaders/vertex.txt"
fragment_sdr_pth = "shaders/fragment.txt"
SQUARE_pth = "models/screen.obj"
OBJECT_SQUARE = 0


################### Model ###################################################
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

################### Control #################################################

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
            
            glfw.poll_events()

            #update scene
            
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

        self.compute_sdr = sdr(vertex_sdr_pth,fragment_sdr_pth,compute_sdr_pth,'GC')

    def set_onetime_uniforms(self) -> None:
        """ Set any uniforms which can simply get set once and forgotten """

        pass

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
        
        
        glFlush()
    
    def destroy(self) -> None:
        """ Free any allocated memory """

        for (_,mesh) in self.meshes.items():
            mesh.destroy()
        self.compute_sdr.deletePgm()

################## Compute shader ############################################

class ComputeShader:

    def __init__(self) -> None:
        pass
        