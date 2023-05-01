bl_info = {
    "name": "HilbertCurve AddOn",
    "author": "",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import sys
print(sys.exec_prefix)
import os
import pip
import bpy
import subprocess
import bmesh


class HilbertLayer : 
    layer_count = 0
    curves = []
    
    
    def __init__(self,mesh):
        self.layer = HilbertLayer.layer_count
        self.mesh = mesh
        self.mesh.name = 'layer' + str(self.layer)
        HilbertLayer.layer_count += 1
        
    #def interpolate(self, resolution = int) :
        #resolution is measured in amount of points
    def show_indices(self):   
        #mesh_obj = find_mesh_by_name(self.name)
        mesh_object = self.mesh
        #bpy.ops.object.select_all(action='DESELECT')
        mesh_object.select_set(True)
        bpy.context.view_layer.objects.active = mesh_object
        
        bpy.ops.object.mode_set(mode='EDIT')
        viewport_3d = get_3d_viewport_space()
        if viewport_3d:
            viewport_3d.overlay.show_extra_indices = True
        else:
            print("3D viewport not found. Cannot enable vertex indices display.")
        #bpy.ops.object.mode_set(mode='OBJECT')

    #def interpolate_all(self,resolution):
        #for curve in curves:
            #interpolate(curve,resolution)
            
            
   
        
        
def get_3d_viewport_space():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        return space
    return None   
def find_mesh_by_name(mesh_name):
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name == mesh_name:
            return obj  
    return None;

def remove_meshes():
    ## clearing current scene
    scene = bpy.context.scene
    HilbertLayer.layer_count = 0;
    for obj in scene.objects:
        if(obj.type == 'MESH'):
            bpy.data.objects.remove(obj, do_unlink=True)
def remove_mesh(name):
    scene = bpy.context.scene
    
def read_obj_file(filename):
    vertices = []
    faces = []

    with open(filename, 'r') as obj_file:
        for line in obj_file:
            tokens = line.split()

            if not tokens:
                continue

            if tokens[0] == 'v':
                vertex = (float(tokens[1]), float(tokens[2]), float(tokens[3]))
                vertices.append(vertex)
            elif tokens[0] == 'f':
                face = (int(tokens[1]) - 1, int(tokens[2]) - 1, int(tokens[3]) - 1)
                faces.append(face)

    return vertices, faces
            
def import_obj_stl( mesh_path, type):
   
    assert (os.path.exists(mesh_path), 'resulted mesh missing')
    remove_meshes()
    
    if(type == 'stl'):
        bpy.ops.import_mesh.stl(filepath=mesh_path)
    ## renaming imports, assuming that different layers of hilbert curve are imported as different layers of object
    if(type == 'obj'):
        object_name = 'hilbert'
        # Open the text file
        obj = bpy.data.objects.new("Object", None)
        # Loop through the lines in the file
        vertices, faces = read_obj_file(mesh_path)
        
        mesh = bpy.data.meshes.new(object_name + '_mesh')# this name is not the layern name
        obj = bpy.data.objects.new(object_name, mesh)

        # Link the object to the current collection
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Create a BMesh object to build the geometry
        bm = bmesh.new()

        # Add vertices and faces to the BMesh object
        for vertex in vertices:
            bm.verts.new(vertex)

        bm.verts.ensure_lookup_table()
        for face in faces:
            bm.faces.new(bm.verts[i] for i in face)

        # Update the mesh with the new geometry and free the BMesh object
        bm.to_mesh(mesh)
        bm.free()

    
    scene = bpy.context.scene
    mesh_object = []
    for obj in scene.objects:
        if(obj.type == 'MESH'):
            mesh_object.append(obj)
            
    object_names = set(obj.name for obj in mesh_object)
    for name in object_names:
        #print('name',name)
        obj =  bpy.data.objects[name]
        curve = HilbertLayer(obj)
        HilbertLayer.curves.append(curve)
    for hy in HilbertLayer.curves:
        hy.show_indices()
    store_hilbert_layers()



def mannually_save(path):
    sol = []
#    for i in range(len(HilbertLayer.curves)): 
#        print(HilbertLayer.curves[i].mesh.name)
#        hc = HilbertLayer.curves[i]
#        obj = bpy.data.objects[hc.mesh.name]
#        mesh = obj.data
#        vertices = [v.co for v in mesh.vertices]
#        sol = sol + vertices 
    hilbert_layers = bpy.context.scene.get('hilbert_layers', [])
    for hl_name in hilbert_layers: 
        if hl_name in bpy.data.objects:
            obj = bpy.data.objects[hl_name]
#            mesh = obj.data
#            world_matrix = obj.matrix_world
#            print('world_matrix', world_matrix)
#            transformed_vertices = [world_matrix @ v.co for v in mesh.vertices]
#            
#            sol = sol + transformed_vertices 
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Get the updated mesh data
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            
            # Get the updated vertex positions
            updated_vertices = [v.co for v in bm.verts]
            sol = sol + updated_vertices
            
            # Return to Object mode
            bpy.ops.object.mode_set(mode='OBJECT')
    #print('sol', sol)
    with open(path, 'w') as obj_file:
        # Write vertices
        for vertex in sol:
            print('vertex',vertex)
            obj_file.write(f"v {vertex.x} {vertex.y} {vertex.z}\n")
    #return sol

# modify vertices mainly gui  stuffs

def create_control_mesh(script_path, mesh_path, order, layers):
     #os.system('python3 ' + script_path + )
     subprocess.run(['python3', script_path, '--mode=create', '--order=' + str(order), '--layer='+str(layers), 
    '--control_stl='+mesh_path])
       
def interpolate_obj(interpolator_path,  original_mesh_path, interpolated_mesh_path, reso,layers ):
    assert (os.path.exists(interpolator_path), 'interpolator module missing')
    print('interpolator path' , interpolator_path )
    
    subprocess.run(['python3', interpolator_path, '--mode=interpolate', '--resolution=' + str(reso), '--layer='+str(layers), 
    '--Ipath='+original_mesh_path, '--Opath='+interpolated_mesh_path])
    
def store_hilbert_layers():
    bpy.context.scene['hilbert_layers'] = [hl.mesh.name for hl in HilbertLayer.curves]






class SimpleUI_OT_SaveMorphedMesh(bpy.types.Operator):
    bl_idname = "simpleui.save_morphed_mesh"
    bl_label = "Save Morphed Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dir = "/Users/seanhuang/Grad/CS582/HilbertCurve/CS582Final/"
        morphed_mesh_path = dir + "morphed_cube.obj"
        print(mannually_save(morphed_mesh_path))
        
        return {'FINISHED'}


class SimpleUI_OT_PerformMainFunctionality(bpy.types.Operator):
    bl_idname = "simpleui.perform_main_functionality"
    bl_label = "Perform Main Functionality"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dir = "/Users/seanhuang/Grad/CS582/HilbertCurve/CS582Final/"
        hilbert_script_path = dir + "FinalProject.py"
        control_mesh_path = dir +"control_cube.obj"
        create_control_mesh(hilbert_script_path, control_mesh_path,2,2)

        import_obj_stl(control_mesh_path, 'obj') 

    
        
        return {'FINISHED'}


#def main(context):
    
    #.obj is mannually imported(order preserved)  wrapped, and stored in HilbertLayer class 
    # currently there can only be 1 layer/obj in the scene  

  

class SimpleUI_PT_Panel(bpy.types.Panel):
    bl_label = "HilbertUI"
    bl_idname = "SIMPLEUI_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Simple UI'

    def draw(self, context):
        layout = self.layout

        # Add buttons
        layout.operator("simpleui.perform_main_functionality", text="Perform Main Functionality")
        layout.operator("simpleui.save_morphed_mesh", text="Save Morphed Mesh")



def menu_func(self, context):
    self.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
def register():
    bpy.utils.register_class(SimpleUI_PT_Panel)
    bpy.utils.register_class(SimpleUI_OT_SaveMorphedMesh)
    bpy.utils.register_class(SimpleUI_OT_PerformMainFunctionality)


def unregister():
    bpy.utils.unregister_class(SimpleUI_PT_Panel)
    bpy.utils.unregister_class(SimpleUI_OT_SaveMorphedMesh)
    bpy.utils.unregister_class(SimpleUI_OT_PerformMainFunctionality)

if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.object.simple_operator()
