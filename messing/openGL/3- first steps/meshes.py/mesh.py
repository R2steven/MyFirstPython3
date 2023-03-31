import json
import numpy as np



class shape_mesh:


    def __init__(self) -> None:
        
        self.load_shapes()


    def load_shapes(self) -> None:
        
        with open('meshes.json','r') as f:
            self.meshes = json.load(f)


    def write_shapes(self,shape:dict) -> None:
        with open('meshes.json','w')as f:
            json.dump(shape,f)


    def set_shape(self,shape:str) -> None:
        self.name = shape
        self.shape = self.meshes[shape]
        self.numVert = self.shape['numVerts']
        self.vertices = np.array(self.shape['vertices'],dtype=np.float32)


sm = shape_mesh()
sm.set_shape('Triangle')
sm.write_shapes({None:None})
