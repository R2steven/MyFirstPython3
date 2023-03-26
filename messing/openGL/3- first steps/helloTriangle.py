import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr


def createShader(vertexfilepath:str, fragmentfilepath:str) -> int:
    """
        Compile and link a shader program from source.

        Parameters:

            vertexFilepath: filepath to the vertex shader source code (relative to this file)

            fragmentFilepath: filepath to the fragment shader source code (relative to this file)
        
        Returns:

            An integer, being a handle to the shader location on the graphics card
    """
    with open(vertexfilepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragmentfilepath,'r') as f:
        fragment_src = f.readlines()

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src,GL_FRAGMENT_SHADER))
    return shader



class App():
    """ The main program """


    def __init__(self):
        """ Set up the program """

        self.set_up_glfw()

        self.make_assets()

        self.get_uniform_locations()

        self.mainLoop()

    def set_up_glfw(self) -> None:
        """Set up the glfw environment"""

        self.screenWidth = 640
        self.screenHeight = 480


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

        self.window =glfw.create_window(
            self.screenWidth,self.screenHeight,"Hello Triangle!",None,None
        )
        glfw.make_context_current(self.window)

    def make_assets(self) -> None:
        """Make any assets used by the App"""
        self.time = 1.0
        self.scale = 1.0
        self.shape_mesh = Rectangle_mesh()
        self.shader = createShader("shaders/vertex.txt", "shaders/fragment.txt")

    def get_uniform_locations(self) -> None:
        """query and store the locations of any uniforms on the shader"""

        glUseProgram(self.shader)
        self.scaleLocation = glGetUniformLocation(self.shader,"scale")

    def mainLoop(self) -> None:
        """Run the App"""

        glClearColor(0.1, 0.2, 0.2, 1)
        (w,h) = glfw.get_framebuffer_size(self.window)
        glViewport(0,0,w,h)
        running = True

        while (running):
            #check events
            if glfw.window_should_close(self.window) \
                or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                running = False
                

            glfw.poll_events()

            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.shader)

            glUniform1f(
                self.scaleLocation,
                self.getScale()
            )

            glBindVertexArray(self.shape_mesh.vao)
            glDrawArrays(GL_TRIANGLE_STRIP,0,self.shape_mesh.vertex_count)

            glFlush()

        self.quit()


    def getScale(self):
        self.time += 1.0*np.pi/18000
        self.scale = np.cos(self.time)
        return np.float32(self.scale)

    def quit(self) -> None:
        """Free any allocated memory"""
        self.shape_mesh.destroy()
        glDeleteProgram(self.shader)
        glfw.terminate()



class Triangle_mesh:

    def __init__(self):

        #x,y,z,r,g,b
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(12))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class Rectangle_mesh:

    def __init__(self):

        #x,y,z,r,g,b
        self.vertices = (
            -1.0, -1.0, 0.0, 1.0, 0.0, 0.0,
             1.0, -1.0, 0.0, 0.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 0.0, 0.0, 1.0,
             1.0, 1.0, 0.0, 1.0, 1.0, 1.0,
        )

        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 4

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(12))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


myapp = App()