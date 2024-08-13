import rhinoscriptsyntax as rs
import scriptcontext as sc
import time
import Rhino.Geometry as rg

def subdivide_curve(curve, new_layer, min_length=1.0):
    try:
        curve_length = rs.CurveLength(curve)
        if curve_length < min_length:
            return 0

        segments = 4 if curve_length > 100 else 3 if curve_length > 50 else 2
        
        points = [rs.EvaluateCurve(curve, rs.CurveParameter(curve, i / segments)) for i in range(segments + 1)]
        
        subdivided_curves = []
        for i in range(len(points) - 1):
            sub_curve = rs.AddLine(points[i], points[i + 1])
            if sub_curve:
                rs.ObjectLayer(sub_curve, new_layer)
                subdivided_curves.append(sub_curve)
        
        rs.DeleteObject(curve)
        
        return len(subdivided_curves)
    except Exception as e:
        print("Error in subdivide_curve: {}".format(e))
        return -1

def subdivide_mesh(mesh_id, new_layer, min_edge_length=1.0):
    try:
        mesh = rs.coercemesh(mesh_id)
        if not mesh:
            return 0

        new_mesh = rg.Mesh()
        vertices = mesh.Vertices.ToPoint3dArray()
        face_indices = []

        for i in range(mesh.Faces.Count):
            face = mesh.Faces[i]
            if face.IsQuad:
                face_indices.append([face.A, face.B, face.C, face.D])
            else:
                face_indices.append([face.A, face.B, face.C])

        new_vertices = list(vertices)
        new_faces = []

        for face in face_indices:
            face_vertices = [vertices[i] for i in face]
            edge_lengths = [face_vertices[i].DistanceTo(face_vertices[(i + 1) % len(face_vertices)]) for i in range(len(face_vertices))]
            
            if all(length <= min_edge_length for length in edge_lengths):
                new_faces.append(face)
            else:
                midpoints = []
                midpoint_indices = []
                for i in range(len(face_vertices)):
                    midpoint = face_vertices[i] + (face_vertices[(i + 1) % len(face_vertices)] - face_vertices[i]) * 0.5
                    if midpoint not in new_vertices:
                        new_vertices.append(midpoint)
                    midpoint_indices.append(new_vertices.index(midpoint))
                    midpoints.append(midpoint)
                
                if len(face) == 4:
                    new_faces.append([face[0], midpoint_indices[0], midpoint_indices[3], face[3]])
                    new_faces.append([midpoint_indices[0], face[1], midpoint_indices[1], midpoint_indices[3]])
                    new_faces.append([midpoint_indices[3], midpoint_indices[1], face[2], face[3]])
                    new_faces.append([midpoint_indices[0], midpoint_indices[1], midpoint_indices[2], midpoint_indices[3]])
                else:
                    new_faces.append([face[0], midpoint_indices[0], midpoint_indices[2]])
                    new_faces.append([midpoint_indices[0], face[1], midpoint_indices[1]])
                    new_faces.append([midpoint_indices[2], midpoint_indices[1], face[2]])
                    new_faces.append([midpoint_indices[0], midpoint_indices[1], midpoint_indices[2]])

        new_vertices_f = [rg.Point3f(v.X, v.Y, v.Z) for v in new_vertices]
        print("Adding {} vertices and {} faces".format(len(new_vertices_f), len(new_faces)))
        
        # Debugging: Print types and sample of vertices
        print("Vertex types and samples:")
        for i, v in enumerate(new_vertices_f[:5]):
            print("Type: {}, Value: {}".format(type(v), v))

        for v in new_vertices_f:
            new_mesh.Vertices.Add(v)

        for f in new_faces:
            if len(f) == 4:
                new_mesh.Faces.AddFace(f[0], f[1], f[2], f[3])
            else:
                new_mesh.Faces.AddFace(f[0], f[1], f[2])

        new_mesh_id = sc.doc.Objects.AddMesh(new_mesh)
        if new_mesh_id:
            rs.ObjectLayer(new_mesh_id, new_layer)
            rs.DeleteObject(mesh_id)
            return 1
        return 0
    except Exception as e:
        print("Error in subdivide_mesh: {}".format(e))
        return -1

def get_object_details(obj):
    details = []
    details.append("GUID: {}".format(obj))
    object_type = rs.ObjectType(obj)
    details.append("Type: {}".format(object_type))
    
    if rs.IsCurve(obj):
        details.append("Object is a curve")
        details.append("Length: {}".format(rs.CurveLength(obj)))
    elif rs.IsMesh(obj):
        details.append("Object is a mesh")
        details.append("Vertices: {}".format(len(rs.MeshVertices(obj))))
    else:
        details.append("Object is neither a curve nor a mesh")
    
    details.append("Layer: {}".format(rs.ObjectLayer(obj)))
    details.append("Name: {}".format(rs.ObjectName(obj) or 'Unnamed'))
    return "\n".join(details)

def divide_all_facades(layer_name, min_curve_length=1.0, min_edge_length=1.0):
    objects = rs.ObjectsByLayer(layer_name)
    if not objects:
        print("No objects found on the layer {}. Exiting.".format(layer_name))
        return

    new_layer = "{}_Subdivided".format(layer_name)
    if not rs.IsLayer(new_layer):
        rs.AddLayer(new_layer)

    total_objects = len(objects)
    curve_count = sum(1 for obj in objects if rs.IsCurve(obj))
    mesh_count = sum(1 for obj in objects if rs.IsMesh(obj))

    print("\nInitial Count:\nTotal objects: {}\nCurves: {}\nMeshes: {}".format(total_objects, curve_count, mesh_count))

    chunk_size = 50
    
    rs.EnableRedraw(False)
    
    total_subdivisions = 0
    processed_objects = 0
    curve_processed_count = 0
    mesh_processed_count = 0
    
    start_time = time.time()
    
    for i in range(0, total_objects, chunk_size):
        chunk = objects[i:i + chunk_size]
        for obj in chunk:
            if rs.IsCurve(obj):
                curve_processed_count += 1
                subdivisions_count = subdivide_curve(obj, new_layer, min_length=min_curve_length)
                if subdivisions_count == -1:
                    print("Terminating script due to error in subdivide_curve.")
                    return
                total_subdivisions += subdivisions_count
            elif rs.IsMesh(obj):
                mesh_processed_count += 1
                subdivisions_count = subdivide_mesh(obj, new_layer, min_edge_length=min_edge_length)
                if subdivisions_count == -1:
                    print("Error encountered. Skipping problematic mesh.")
                    continue  # Skip the problematic mesh and continue processing
                total_subdivisions += subdivisions_count
        
        processed_objects += len(chunk)
        rs.EnableRedraw(True)
        sc.doc.Views.Redraw()
        rs.EnableRedraw(False)
        sc.escape_test(False)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    rs.EnableRedraw(True)
    print("\nFinal Report:\nProcessed {} objects: {} curves, {} meshes".format(total_objects, curve_processed_count, mesh_processed_count))
    print("Created {} subdivided objects on layer '{}'".format(total_subdivisions, new_layer))
    print("Processing time: {:.2f} seconds".format(processing_time))

if __name__ == "__main__":
    layer_name = rs.GetString("Enter the name of the layer containing facades to subdivide", rs.CurrentLayer())
    if layer_name and rs.IsLayer(layer_name):
        divide_all_facades(layer_name)
    else:
        print("Invalid layer name. Exiting.")
