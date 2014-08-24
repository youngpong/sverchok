# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import parser
import mathutils
from mathutils import Vector
from bpy.props import StringProperty, BoolProperty
from node_tree import SverchCustomTreeNode, StringsSocket, VerticesSocket
from data_structure import (updateNode, Vector_generate, SvSetSocketAnyType, SvGetSocketAnyType)

class SvRayCastNode(bpy.types.Node, SverchCustomTreeNode):
    ''' RayCast Object '''
    bl_idname = 'SvRayCastNode'
    bl_label = 'raycast'
    bl_icon = 'OUTLINER_OB_EMPTY'


    
    wspinput = BoolProperty(name='world coord', description='Translate inputs and outputs to world coordinates', default=True, update=updateNode)
    
    formula = StringProperty(name='formula', description='name of object to operate on', default='Cube', update=updateNode)

    def draw_buttons(self, context, layout):
        layout.prop(self, "formula", text="")
        row = layout.row(align=True)
        row.prop(self, "wspinput", text="Use world coord")

        
    def init(self, context):
        self.inputs.new('VerticesSocket', 'start', 'start')
        self.inputs.new('VerticesSocket', 'end', 'end')

        self.outputs.new('VerticesSocket', "HitP", "HitP")
        self.outputs.new('VerticesSocket', "HitNorm", "HitNorm")
        self.outputs.new('StringsSocket', "PoligIND", "PoligIND")
    
    def update(self):
        
        out=[]
        OutLoc=[]
        OutNorm=[]
        FaceINDEX=[]

        
        obj= bpy.data.objects[self.formula]
        
        if 'start' in self.inputs and self.inputs['start'].links and \
           type(self.inputs['start'].links[0].from_socket) == VerticesSocket and \
             'end' in self.inputs and self.inputs['end'].links and \
                type(self.inputs['end'].links[0].from_socket) == VerticesSocket:
                   st = Vector_generate(SvGetSocketAnyType(self, self.inputs['start']))
                   en = Vector_generate(SvGetSocketAnyType(self, self.inputs['end']))
                   start= [Vector(x) for x in st[0]]
                   end= [Vector(x) for x in en[0]]
                   if self.wspinput:
                       start= [ i-obj.location for i in start ]
                       end= [ i-obj.location for i in end ]
        
                   i=0
                   while i< len(end):
                       out.append(obj.ray_cast(start[i],end[i]))
                       i= i+1


                   for i in out:
                       
                       OutNorm.append(i[1][:])
                       FaceINDEX.append(i[2])
                       if self.wspinput:
                           OutLoc.append( (i[0]+obj.location)[:] )
                       else:
                           OutLoc.append(i[0][:])


                   if self.outputs['HitP'].links:
                       SvSetSocketAnyType(self, 'HitP', [OutLoc])
                   if self.outputs['HitNorm'].links:
                       SvSetSocketAnyType(self, 'HitNorm', [OutNorm])
                   if self.outputs['PoligIND'].links:
                       SvSetSocketAnyType(self, 'PoligIND', [FaceINDEX])





    def update_socket(self, context):
        self.update()

def register():
    bpy.utils.register_class(SvRayCastNode)

def unregister():
    bpy.utils.unregister_class(SvRayCastNode)
