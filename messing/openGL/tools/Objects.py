from OpenGL.GL import *
import numpy as np
from PIL import Image

"""
    load objects, materials, etc from .obj and .mtl files
"""

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