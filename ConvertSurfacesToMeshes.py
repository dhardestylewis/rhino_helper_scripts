import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino.Geometry as rg
import time

def convert_surfaces_to_meshes(layer_name, new_layer, batch_size=50):
    objects = rs.ObjectsByLayer(layer_name)
    if not objects:
        print("No objects found on the layer {0}. Exiting.".format(layer_name))
        return

    if not rs.IsLayer(new_layer):
        rs.AddLayer(new_layer)

    total_objects = len(objects)
    surface_count = sum(1 for obj in objects if rs.IsSurface(obj))
    converted_count = 0
    
    rs.EnableRedraw(False)
    
    start_time = time.time()
    
    for i in range(0, total_objects, batch_size):
        batch = objects[i:i + batch_size]
        for obj in batch:
            if rs.IsSurface(obj):
                # Get the surface geometry
                surface = rs.coercebrep(obj)
                if surface:
                    # Convert surface to mesh
                    meshes = rg.Mesh.CreateFromBrep(surface, rg.MeshingParameters.Default)
                    if meshes:
                        for mesh in meshes:
                            mesh_id = sc.doc.Objects.AddMesh(mesh)
                            if mesh_id:
                                rs.ObjectLayer(mesh_id, new_layer)
                                converted_count += 1
                        rs.DeleteObject(obj)
        
        rs.EnableRedraw(True)
        sc.doc.Views.Redraw()
        rs.EnableRedraw(False)
        sc.escape_test(False)  # Allow user to cancel the script
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    rs.EnableRedraw(True)
    print("\nFinal Report:")
    print("Processed {0} surfaces".format(surface_count))
    print("Converted {0} surfaces to meshes on layer '{1}'".format(converted_count, new_layer))
    print("Processing time: {0:.2f} seconds".format(processing_time))

if __name__ == "__main__":
    layer_name = rs.GetString("Enter the name of the layer containing surfaces to convert", rs.CurrentLayer())
    if layer_name and rs.IsLayer(layer_name):
        new_layer = rs.GetString("Enter the name of the new layer for meshes", layer_name + "_Meshes")
        convert_surfaces_to_meshes(layer_name, new_layer)
    else:
        print("Invalid layer name. Exiting.")
