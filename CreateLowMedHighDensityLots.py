
import rhinoscriptsyntax as rs

def create_lots():
    # Define the lot sizes (width, length)
    lot_sizes = [
        (25, 95),  # Low density
        (40, 95),  # Medium density
        (100, 95)  # High density
    ]
    
    # Define the spacing between lots
    spacing_x = 20
    spacing_y = 20
    
    # Starting position
    start_x = 0
    start_y = 0
    
    # Create the lots
    for i in range(2):  # Rows
        for j in range(3):  # Columns
            width, length = lot_sizes[j]
            # Calculate the position for each rectangle
            x = start_x + j * (width + spacing_x)
            y = start_y + i * (length + spacing_y)
            # Create the rectangle
            rect_pts = [
                (x, y, 0),
                (x + width, y, 0),
                (x + width, y + length, 0),
                (x, y + length, 0),
                (x, y, 0)
            ]
            rs.AddPolyline(rect_pts)

# Run the script
create_lots()
