class Node:
    def __init__(self,rad,pos,vel):
        self.rad=rad
        self.ppos=pos-vel
        self.pos=pos
    def update(self,dt):
        vel=self.pos-self.ppos
        self.pos+=vel*dt
        self.ppos=self.pos-vel
class Link:
    pass
class System:
    def __init__(self):
        self.nodes=[]
    def add(self,node):
        self.nodes.append(node)
    def update(self,dt):
        for node in self.nodes:
            node.update(dt)