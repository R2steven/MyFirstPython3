import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
from PIL import Image


class Shader():
    """
        Compile and use Shader
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



class App():
    """ The main program """

    screenWidth = 640
    screenHeight = 480
    vertexPath = 'shaders/texvert.txt'
    fragmentPath = 'shaders/texfrag.txt'


    def __init__(self) -> None:

        self.set_up_glfw()

        self.make_assets()

        self.mainLoop()

    def set_up_glfw(self) -> None:
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
            self.screenWidth,self.screenHeight,"Take a Texture!",None,None
        )
        glfw.make_context_current(self.window)

    def make_assets(self) -> None:
        self.shader = Shader(self.vertexPath,self.fragmentPath)
        self.shape_mesh1 = Triangle()
        self.shader.setFloat('scale',np.float32(1.0))
        self.time = 0.0
        self.material = Material('textures/wall.jpg')
       
    def mainLoop(self): 
        """Run the App"""

        glClearColor(0.1,0.2,0.2,1.0)
        (w,h) = glfw.get_framebuffer_size(self.window)
        glViewport(0,0,w,h)
        running = True

        while (running):
            if(glfw.window_should_close(self.window) or
               glfw.get_key(self.window,GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS):
                running = False

            glfw.poll_events()

            glClear(GL_COLOR_BUFFER_BIT)
            self.shader.use()
            self.material.use()
            glBindVertexArray(self.shape_mesh1.vao)

            glDrawArrays(GL_TRIANGLES,0,self.shape_mesh1.vertex_Count)

            glfw.swap_buffers(self.window)
        
        self.quit()

    def quit(self) -> None:
        self.shape_mesh1.destroy()
        self.shader.deletePgm()
        glfw.terminate()


class Shape_mesh:
    """
        load a shape into gl buffers
        vao format: [[x,y,z,r,g,b],...]
    """

    def __init__(self,vertices,vertCount) -> None:
        
        self.vertices = np.array(vertices,dtype=np.float32) #stored in float32 np.array
        self.vertex_Count = vertCount

        self.gen_Buffers()

    def gen_Buffers(self) -> None:
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)

        self.gen_attrib_pointer()#useless, can be modified for more pointers

    def gen_attrib_pointer(self) -> None:
        glEnableVertexAttribArray(0) #dict input?
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,2,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(24))

    def destroy(self):
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Triangle(Shape_mesh):
    """
        generate a triangle mesh
    """
    vertices = (
                   -0.5,-0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
                    0.5,-0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0,
                    0.0, 0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 1.0
    )
    
    def __init__(self) -> None:
        self.vertex_Count = 3
        super().__init__(self.vertices,self.vertex_Count)


class Material:

    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)

        with Image.open(filepath,'r') as image:
            image_width,image_height=image.size
            image = image.convert("RGBA")
            image_data = bytes(image.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1,(self.texture,))





myapp = App()



        