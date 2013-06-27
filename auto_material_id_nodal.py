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

def rmMaterialsUnused():
    mat_list = []
    escenas = bpy.data.scenes
    # recorriendo todas las escenas en busca de materiales usados:
    for i in range(len(escenas)):
        for ob in escenas[i].objects:
            # si es de tipo objeto entonces
            if ob.type == 'MESH' or ob.type == 'SURFACE' or ob.type == 'META':
                if ob.data.materials == '' or len(ob.material_slots.items()) != 0:
                    # si no esta vacio o tiene mas de 0 slots entonces me lo recorro y voy agregando los materiales al array
                    for ms in ob.material_slots:
                        mat_list.append(ms.material)
                        
    # limpiando lista de repetidos:
    def rmRepetidos(listado):
        listado = list(set(listado)) # elimina duplicados
        return listado
    
    # limpiando lista de repetidos:
    mat_list = rmRepetidos(mat_list)
    
    for m in bpy.data.materials:
        # si no estan en mi lista es que no estan siendo usados, por lo tanto los elimino:
        if m not in mat_list:
            if m.use_fake_user == False: # respetaremos los fake
                m.user_clear()
                bpy.data.materials.remove(m)



def materialIDNodal():
    # contexto:
    cs = bpy.context.scene

    # activamos los nodos:
    cs.use_nodes = True

    # nombre de el nuevo clon de escena:
    tipo = "Material_ID"

    # escenas 
    escenas = []
    for s in bpy.data.scenes:
        escenas.append(s)

    # si no esta el nombre del clon en las escenas:    
    if tipo not in escenas:

        # clonamos la escena actual:
        bpy.ops.scene.new(type='FULL_COPY')

        # capturo el nombre de la escena actual:
        cual = bpy.context.scene.name

        # me recorro las ecenas en busca de la escena actual:
        for s in bpy.data.scenes:
            if s.name == cual: #<-- si es la actual
                s.name = tipo #<-- seteamos el nuevo nombre

        # compruebo la escena:
        def chequeoEscena(): #<-- si la escena actual se llama como el nuevo clon, entonces true 
            if bpy.context.scene.name == tipo:
                return True
            else:
                return False

        # si es true continuamos con el resto del script:
        if chequeoEscena():                        
            def getMateriales():
                # obteniendo todos los nombres de los materiales de todos los objetos de la escena actual:
                mat_list = []
                for ob in bpy.data.scenes[bpy.context.scene.name].objects:
                    if ob.type == 'MESH' or ob.type == 'SURFACE' or ob.type == 'META':
                        if ob.data.materials == '' or len(ob.material_slots.items()) != 0:
                            for ms in ob.material_slots:
                                mat_list.append(ms.material)
                # limpiando lista de repetidos:
                def rmRepetidos(listado):
                    listado = list(set(listado)) # elimina duplicados
                    return listado
                # limpiando lista de repetidos:
                mat_list = rmRepetidos(mat_list)
                return mat_list
            
            # restore all id:
            def resetAutomaticId():
                # para resetear todo a cero:
                st = 0
                for mt in bpy.data.materials:
                    if mt in getMateriales():
                        mt.pass_index = st
            
            resetAutomaticId()
            
            # activando material id en render layers:
            rls = bpy.context.scene.render.layers.active
            rls.use_pass_material_index = True
            
            def automaticId():
                # para dar auto ids materials:
                st = 0
                for mt in bpy.data.materials:
                    if mt in getMateriales():
                        mt.pass_index = st=st+1
                
               
            def crearNodosNecesarios():
            
                # switch on nodes
                bpy.context.scene.use_nodes = True
                tree = bpy.context.scene.node_tree
            
                # clear default nodes
                for n in tree.nodes:
                    tree.nodes.remove(n)
            
                # create input render layer node
                rl = tree.nodes.new('CompositorNodeRLayers')
                #rl = bpy.ops.node.add_node(type="CompositorNodeRLayers", use_transform=True)
                rl.location = 0,0
            
                # averiguando cuantos ids hay y cuales son:
                ##########################################################
                ids = []
                for mt in bpy.data.materials:
                    if mt.pass_index > 0 and mt.users != 0 and mt in getMateriales():
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
                inc = 0.001 #<-- incremento de values
                for i in range(len(ids)):
                    # create ID_MASK node
                    idm = tree.nodes.new('CompositorNodeIDMask')
                    idm.location = 300,-i*150
                    idm.index = ids[i]
            
                    # create MIX node
                    mx = tree.nodes.new('CompositorNodeMixRGB')
                    mx.location = 600,-i*300
                    mx.blend_type = 'MULTIPLY'
                    for i in range(len(mx.inputs[1].default_value)):
                            mx.inputs[1].default_value[i] = random.random() + inc  #<-- mas el incremento
                            
                    #0 es r 1 es g y 2 es b y el 3 el alpha
                    mx.inputs[1].default_value[3] = 1
                    inc = inc + 0.001 #<-- por cada pasada se incrementa mas el value
            
                # Creando adds
                count_ids = len(ids)
                for i in range(count_ids-1):
                    # create MIX node
                    mxa = tree.nodes.new('CompositorNodeMixRGB')
                    mxa.location = 900+i*250,-i*300
                    mxa.blend_type = 'ADD'
            
                # create output node
                comp = tree.nodes.new('CompositorNodeComposite')
                comp.location = 2500,0
            
                # create VIEWER node
                vie = tree.nodes.new("CompositorNodeViewer")
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
                if numero_de_mix_a > 0: # si hay mas de 1 mix add:
                    links.new(c_nodos_mix_a[numero_de_mix_a-1].outputs[0],comp.inputs[0])
                    links.new(c_nodos_mix_a[numero_de_mix_a-1].outputs[0],vie.inputs[0])
                else: # si no hay mix add por que solo hay 1 unico id:
                    links.new(c_nodos_mix_m[0].outputs[0],comp.inputs[0])
                    links.new(c_nodos_mix_m[0].outputs[0],vie.inputs[0])
            
            ############################################################
            # materialIDNodatl options:
            ############################################################
            # for restore all ids to 0 value, uncoment this:
            #resetAutomaticId()
            # an coment automaticId, and crearNodosNecesarios functions
            ############################################################
            #
            automaticId()
            ################################################################
            # IMPORTANT
            # if you use my automaticId function, you need re-rendered the
            # scene for can get your news ids
            ################################################################
            #
            # Creating all nodes:
            crearNodosNecesarios()
            # end materialIDNodatl options #############################
            ############################################################
            cs.render.engine = 'BLENDER_RENDER'

# use for create material id nodes:
materialIDNodal()

#############################################################################
# If you used this script several times and doubled too many materials
# times you can clean some materials using this function: rmMaterialsUnused()
#############################################################################
rmMaterialsUnused()
