'''
Copyright (c) 2012 Jorge Hernandez - Melendez

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
import bpy, math, random

escenas = bpy.data.scenes
#materiales=bpy.data.materials
if "Material_ID" not in escenas:
    bpy.ops.scene.new(type='FULL_COPY')
    bpy.context.scene.name = "Material_ID"
    bpy.ops.object.select_all(action='DESELECT')
    scn = bpy.context.scene
    cntxt = bpy.context
    def chequeoEscena():
        if scn.name == "Material_ID":
            return True
        else:
            return False
    if chequeoEscena(): 
        
        # activando material id en render layers:
        rls = bpy.context.scene.render.layers.active
        rls.use_pass_material_index = True
        
        def automaticId():
            # para dar auto ids materials:
            st = 1
            for mt in bpy.data.materials:
               mt.pass_index = st=st+1
            
        def resetAutomaticId():
            # para resetear todo a cero:
            st = 0
            for mt in bpy.data.materials:
                mt.pass_index = st
           
        def crearNodosNecesarios():
        
            # switch on nodes
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
        
            # clear default nodes
            for n in tree.nodes:
                tree.nodes.remove(n)
        
            # create input render layer node
            rl = tree.nodes.new('R_LAYERS')
            rl.location = 0,0
        
            # averiguando cuantos ids hay y cuales son:
            ##########################################################
            ids = []
            for mt in bpy.data.materials:
                if mt.pass_index > 0 and mt.users != 0:
                    ids.append(mt.pass_index)
        
            def rmRepetidos(listado):
                listado = list(set(listado)) # <-- elimina duplicados
                return listado
            
            ids = rmRepetidos(ids) # <-- limpiando lista de repetidos
            ##########################################################
        
                     
            # obteniendo la posicion del slot de IndexMA en el render layers:
            def getPositionMID():
                for i in range(len(rl.outputs)):
                    if rl.outputs[i].name == 'IndexMA':
                        return i
        
            # Creando los nodos necesarios:
            for i in range(len(ids)):
                # create ID_MASK node
                idm = tree.nodes.new('ID_MASK')
                idm.location = 300,-i*150
                idm.index = ids[i]
        
                # create MIX node
                mx = tree.nodes.new('MIX_RGB')
                mx.location = 600,-i*300
                mx.blend_type = 'MULTIPLY'
                for i in range(len(mx.inputs[1].default_value)-1):
                    mx.inputs[1].default_value[i] = random.random()
        
            # Creando adds
            count_ids = len(ids)
            for i in range(count_ids-1):
                # create MIX node
                mxa = tree.nodes.new('MIX_RGB')
                mxa.location = 900+i*250,-i*300
                mxa.blend_type = 'ADD'
        
            # create output node
            comp = tree.nodes.new('COMPOSITE')
            comp.location = 2500,0
        
            # create VIEWER node
            vie = tree.nodes.new("VIEWER")
            vie.location = 2500,170
        
        
            # LINKANDO:
            links = tree.links
        
            #sabiendo cuantos nodos id hay:
            c_nodos_id = []
            for i in range(len(tree.nodes)):
                # buscamos si contiene la palabra o parte de la palabra:
                if tree.nodes[i].name.find('ID Mask') >= 0:
                    c_nodos_id.append(tree.nodes[i])
                    
            #sabiendo cuantos nodos mix multiply hay:
            c_nodos_mix_m = []
            for i in range(len(tree.nodes)):
                if tree.nodes[i].name.find('Mix') >= 0: # <-- buscamos si contiene parte de la palabra Mix
                    if tree.nodes[i].blend_type == 'MULTIPLY':
                        c_nodos_mix_m.append(tree.nodes[i])
        
            #sabiendo cuantos nodos mix add hay:
            c_nodos_mix_a = []
            for i in range(len(tree.nodes)):
                if tree.nodes[i].name.find('Mix') >= 0: # <-- buscamos si contiene parte de la palabra Mix
                    if tree.nodes[i].blend_type == 'ADD':
                        c_nodos_mix_a.append(tree.nodes[i])
        
        
            numero_de_nodos_id = len(c_nodos_id)
        
            # links de render layers a id mask y de id mask a mix multiply:
            try:
                for i in range(numero_de_nodos_id):
                    links.new(rl.outputs[getPositionMID()],c_nodos_id[i].inputs[0])
                    links.new(c_nodos_id[i].outputs[0],c_nodos_mix_m[i].inputs[2])
            except:
                pass
        
            numero_de_mix_m = len(c_nodos_mix_m)
            numero_de_mix_a = len(c_nodos_mix_a)
        
            # links de mix a add:
            for i in range(numero_de_mix_m):
                try:
                    # lineas correctas izk a der abajo arriba:
                    links.new(c_nodos_mix_m[i].outputs[0],c_nodos_mix_a[i-1].inputs[2])
                    if i <= 0: # la primera pasada para crear el puente arriba abajo izk a der:
                        links.new(c_nodos_mix_m[i].outputs[0],c_nodos_mix_a[i].inputs[1])
                    else: # para el resto de pasadas enganchar input del add i con el output del add anterior:
                        links.new(c_nodos_mix_a[i].inputs[1],c_nodos_mix_a[i-1].outputs[0])
                except:
                    pass
        
            # conectando viewer y composite:
            links.new(c_nodos_mix_a[numero_de_mix_a-1].outputs[0],comp.inputs[0])
            links.new(c_nodos_mix_a[numero_de_mix_a-1].outputs[0],vie.inputs[0])
        
        
        ############################################################
        # for restore all ids to 0 value, uncoment this:
        #resetAutomaticId()
        # an coment automaticId, and crearNodosNecesarios functions
        ############################################################
        
        automaticId()
        ################################################################
        # IMPORTANT
        # if you use my automaticId function, you need re-rendered the
        # scene for can get your news ids
        ################################################################
        
        # Creating all nodes:
        crearNodosNecesarios()