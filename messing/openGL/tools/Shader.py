from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader

"""
    basic shader management"""

class Shader():
    """
        Compile and use Shader
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
        if not(name in self.unifNames.keys()):
            self.unifNames[name] = glGetUniformLocation(self.shader,name)
        glUniform1i(self.unifNames[name],value)

    def setInt(self, name:str, value:int) -> None:
        self.use()
        if not(name in self.unifNames.keys()):
            self.unifNames[name] = glGetUniformLocation(self.shader,name)
        glUniform1i(self.unifNames[name], value)

    def setFloat(self, name:str, value) -> None:
        self.use()
        if not(name in self.unifNames.keys()):
            self.unifNames[name] = glGetUniformLocation(self.shader,name)
        glUniform1f(self.unifNames[name], value)
    
    def setVec2f(self,name:str, value) -> None:
        self.use()
        if not(name in self.unifNames.keys()):
            self.unifNames[name] = glGetUniformLocation(self.shader,name)
        glUniform2f(self.unifNames[name], value[0], value[1])

    def setMat4fv(self, name:str, Matrix4fv) -> None:
        self.use()
        if not(name in self.unifNames.keys()):
            self.unifNames[name] = glGetUniformLocation(self.shader,name)
        glUniformMatrix4fv(self.unifNames[name],1,GL_FALSE,Matrix4fv)

    def deletePgm(self):
        glDeleteProgram(self.shader)