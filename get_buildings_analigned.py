import rhinoscriptsyntax as rs
import Rhino.Geometry as rg

def extract_buildings_within_bounding_box_and_save():
    # Define the bounding box coordinates
    min_x = min(1026747.722, 1026944.545, 1027687.389, 1027465.610)
    max_x = max(1026747.722, 1026944.545, 1027687.389, 1027465.610)
    min_y = min(189233.367, 188605.482, 188896.548, 189497.249)
    max_y = max(189233.367, 188605.482, 188896.548, 189497.249)

    # Get all objects from the relevant layers
    all_objects = rs.ObjectsByLayer("Building_Facade") + rs.ObjectsByLayer("Building_FootPrint")
    
    # Filter objects within the bounding box
    filtered_objects = []
    for obj in all_objects:
        bbox = rs.BoundingBox(obj)
        if bbox:
            obj_min_x = min(point.X for point in bbox)
            obj_max_x = max(point.X for point in bbox)
            obj_min_y = min(point.Y for point in bbox)
            obj_max_y = max(point.Y for point in bbox)
            
            # Check if object's bounding box intersects with our bounding box
            if (obj_min_x <= max_x and obj_max_x >= min_x and
                obj_min_y <= max_y and obj_max_y >= min_y):
                filtered_objects.append(obj)
    
    # Check if any objects were found
    if not filtered_objects:
        print("No Building_Facade or Building_FootPrint objects found within the bounding box.")
        return
    
    # Select the filtered objects
    rs.SelectObjects(filtered_objects)
    
    # Report results
    print("Selected {} objects within the specified bounding box.".format(len(filtered_objects)))
    
    # Save selected objects to a new file
    save_path = rs.SaveFileName("Save selected objects", "Rhino 3D Models (*.3dm)|*.3dm")
    if save_path:
        rs.SelectObjects(filtered_objects)  # Ensure objects are selected
        rs.Command('_-Export "{}" _Enter'.format(save_path))
        print("Selected objects saved to: {}".format(save_path))
    else:
        print("Save operation cancelled.")

# Run the main function
if __name__ == "__main__":
    extract_buildings_within_bounding_box_and_save()
