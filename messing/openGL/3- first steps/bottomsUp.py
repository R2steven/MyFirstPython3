import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr


class Shader():
    """
        Compile and use shader
    """

    def __init__(self, vertexPath:str, fragmentPath:str) -> None:
        
        self.createShader(vertexPath,fragmentPath)
        self.checkCompileErrors(self.shader,'PROGRAM')


    def createShader(self, vertexPath:str, fragmentPath:str) -> None:
        with open(vertexPath,'r') as f:
            vertex_src = f.readlines()
        
        with open(fragmentPath,'r') as f:
            fragment_src = f.readlines()
        
        self.shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                                compileShader(fragment_src,GL_FRAGMENT_SHADER))
        
    def checkCompileErrors(self,shader,Ptype:str) -> None:

        success = 0
        
        if(Ptype != 'PROGRAM'):
            success = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if(not success):
                print(glGetShaderInfoLog(shader).decode())

        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS)
            if(not success):
                print(glGetProgramInfoLog(shader))
    
    def use(self) -> None:
        glUseProgram(self.shader)

    def setBool(self, name:str, value:bool) -> None:
        self.use()
        glUniform1i(glGetUniformLocation(self.shader,name), int(value))

    def setInt(self, name:str, value:int) -> None:
        glUniform1i(glGetUniformLocation(self.shader,name), value)

    def setFloat(self, name:str, value:np.float32) -> None:
        glUniform1f(glGetUniformLocation(self.shader,name), value)

    def setMat4fv(self, name:str, Matrix4fv:pyrr.matrix44) -> None:
        glUniformMatrix4fv(glGetUniformLocation(self.shader,name),Matrix4fv)

    def deletePgm(self):
        glDeleteProgram(self.shader)

    

class App():
    """ The main program """
    screenWidth = 640
    screenHeight = 480
    vertexPath = 'shaders/vertex.txt'
    fragmentPath = 'shaders/fragment.txt'
    vertices1 = (
            -0.9, -0.5, 0.0, 0.0, 1.0, 0.0,
             0.0, -0.5, 0.0, 0.0, 1.0, 0.0,
           -0.45,  0.5, 0.0, 0.0, 1.0, 0.0
        )
    vertices2 = (   
             0.9, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.0, -0.5, 0.0, 1.0, 0.0, 0.0,
            0.45,  0.5, 0.0, 1.0, 0.0, 0.0,
        )
    indices1 = (0,1,2)
    indices2 = (0,1,2)

    def __init__(self) -> None:

        self.set_up_glfw()

        self.make_assets()

        self.mainLoop()

    def set_up_glfw(self):
        """Set up the glfw environment"""

        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE,
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE
        )
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,True)

        self.window = glfw.create_window(
            self.screenWidth,self.screenHeight,"Hello Triangle!",None,None
        )
        glfw.make_context_current(self.window)

    def make_assets(self) -> None:
        self.shader = Shader(self.vertexPath,self.fragmentPath)
        self.shape_mesh1 = Shape_mesh(self.vertices1,self.indices1)
        self.shape_mesh2 = Shape_mesh(self.vertices2, self.indices2)
        self.time = 0.0

    def mainLoop(self):
        """Run the App"""

        glClearColor(0.1,0.2,0.2,1.0)
        (w,h) = glfw.get_framebuffer_size(self.window)
        glViewport(0,0,w,h)
        running = True

        while(running):
            if(glfw.window_should_close(self.window) or
                glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS):
                    
                    running = False
            
            glfw.poll_events()

            glClear(GL_COLOR_BUFFER_BIT)
            self.shader.use()
            self.shader.setFloat("scale",self.getScale())

            #glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.shape_mesh.ebo)
            glBindVertexArray(self.shape_mesh1.vao)
            
            
            glDrawArrays(GL_TRIANGLES,0,self.shape_mesh1.vertex_count)
            #glDrawElements(GL_TRIANGLES,self.shape_mesh.vertex_count,GL_UNSIGNED_INT,None) #needs bindbuffer(ebo) and this None!!


            glBindVertexArray(self.shape_mesh2.vao)
            glDrawArrays(GL_TRIANGLES,0,self.shape_mesh2.vertex_count)
            glFlush()
            glfw.swap_buffers(self.window)

        self.quit()

    def quit(self) -> None:
        self.shape_mesh1.destroy()
        self.shape_mesh2.destroy()
        self.shader.deletePgm()
        glfw.terminate()

            
    
    def getScale(self):
        self.time += 1.0*np.pi/18000
        self.scale = np.cos(self.time)
        return np.float32(self.scale)

class Shape_mesh:

    def __init__(self,vertices,indices) -> None:

        #x,y,z,r,g,b
        self.vertices = vertices
        self.indices = indices

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.indices = np.array(indices,dtype=np.uint32)

        self.vertex_count = 3
        
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,self.indices.nbytes,self.indices,GL_STATIC_DRAW)
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
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(2,(self.vbo, self.ebo))


myapp = App()