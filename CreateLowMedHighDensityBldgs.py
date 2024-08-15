import rhinoscriptsyntax as rs

def create_buildings():
    # Lot dimensions and properties
    lot_sizes = [(25, 95), (40, 95), (100, 95)]  # Low, medium, high density
    far_limits = [0.9, 2.0, 7.52]  # FAR limits for low, medium, high density
    min_floor_height = 10  # Minimum floor height in feet
    num_floors = 4  # Number of floors for medium and high-density buildings
    height_high = 85  # Maximum height for high-density buildings

    # Side and front/rear yard requirements
    side_yard_low = 4
    front_yard = 5
    rear_yard = 30
    street_width = 35
    
    start_x = 0
    start_y = 0
    spacing_x = 20
    spacing_y = 20

    for i in range(2):  # Rows
        for j in range(3):  # Columns
            lot_width, lot_length = lot_sizes[j]
            lot_area = lot_width * lot_length
            max_floor_area = far_limits[j] * lot_area

            # Calculate the base position for each lot
            x = start_x + j * (lot_width + spacing_x)
            y = start_y + i * (lot_length + spacing_y)
            
            if j == 0:  # Low density
                building1_width = lot_width - side_yard_low
                building1_length = lot_length - front_yard - rear_yard
                building1_area = building1_width * building1_length
                building1_height = min_floor_height  # Assume single-floor buildings for low density

                rs.AddBox([(x, y + front_yard, 0), (x + building1_width, y + front_yard, 0),
                           (x + building1_width, y + front_yard + building1_length, 0), (x, y + front_yard + building1_length, 0),
                           (x, y + front_yard, building1_height), (x + building1_width, y + front_yard, building1_height),
                           (x + building1_width, y + front_yard + building1_length, building1_height), (x, y + front_yard + building1_length, building1_height)])
                
                building2_width = lot_width - 2 * side_yard_low
                building2_area = building2_width * building1_length
                building2_height = min_floor_height  # Assume single-floor buildings for low density

                rs.AddBox([(x + side_yard_low, y + front_yard, 0), (x + side_yard_low + building2_width, y + front_yard, 0),
                           (x + side_yard_low + building2_width, y + front_yard + building1_length, 0), (x + side_yard_low, y + front_yard + building1_length, 0),
                           (x + side_yard_low, y + front_yard, building2_height), (x + side_yard_low + building2_width, y + front_yard, building2_height),
                           (x + side_yard_low + building2_width, y + front_yard + building1_length, building2_height), (x + side_yard_low, y + front_yard + building1_length, building2_height)])
            
            elif j == 1:  # Medium density
                if i == 0:  # Front building
                    total_floor_area = max_floor_area / num_floors
                    current_height = 0
                    building_width = lot_width * 0.6

                    for k in range(num_floors):
                        floor_height = min_floor_height
                        floor_area = building_width * (lot_length - front_yard - rear_yard)

                        if floor_area > total_floor_area:
                            # Adjust the footprint to meet the FAR requirement
                            building_width = total_floor_area / (lot_length - front_yard - rear_yard)
                            floor_area = total_floor_area

                        rs.AddBox([(x + (lot_width - building_width) / 2, y + front_yard, current_height),
                                   (x + (lot_width + building_width) / 2, y + front_yard, current_height),
                                   (x + (lot_width + building_width) / 2, y + front_yard + lot_length - rear_yard, current_height),
                                   (x + (lot_width - building_width) / 2, y + front_yard + lot_length - rear_yard, current_height),
                                   (x + (lot_width - building_width) / 2, y + front_yard, current_height + floor_height),
                                   (x + (lot_width + building_width) / 2, y + front_yard, current_height + floor_height),
                                   (x + (lot_width + building_width) / 2, y + front_yard + lot_length - rear_yard, current_height + floor_height),
                                   (x + (lot_width - building_width) / 2, y + front_yard + lot_length - rear_yard, current_height + floor_height)])
                        
                        building_width *= 0.9
                        current_height += floor_height

                if i == 1:  # Back building (mirrored inverted pyramid style)
                    current_height = 0
                    building_width = lot_width * 0.6 * (0.9 ** 3)

                    for k in range(num_floors):
                        floor_height = min_floor_height
                        floor_area = building_width * (lot_length - front_yard - rear_yard)

                        if floor_area > total_floor_area:
                            # Adjust the footprint to meet the FAR requirement
                            building_width = total_floor_area / (lot_length - front_yard - rear_yard)
                            floor_area = total_floor_area

                        rs.AddBox([(x + (lot_width - building_width) / 2, y + front_yard, current_height),
                                   (x + (lot_width + building_width) / 2, y + front_yard, current_height),
                                   (x + (lot_width + building_width) / 2, y + front_yard + lot_length - rear_yard, current_height),
                                   (x + (lot_width - building_width) / 2, y + front_yard + lot_length - rear_yard, current_height),
                                   (x + (lot_width - building_width) / 2, y + front_yard, current_height + floor_height),
                                   (x + (lot_width + building_width) / 2, y + front_yard, current_height + floor_height),
                                   (x + (lot_width + building_width) / 2, y + front_yard + lot_length - rear_yard, current_height + floor_height),
                                   (x + (lot_width - building_width) / 2, y + front_yard + lot_length - rear_yard, current_height + floor_height)])
                        
                        building_width /= 0.9
                        current_height += floor_height

            elif j == 2:  # High density
                total_floor_area = max_floor_area / num_floors
                current_height = 0

                for k in range(num_floors):
                    building_width = lot_width * (1 - 0.1 * k)
                    building_length = lot_length * (1 - 0.1 * k) - rear_yard
                    floor_height = min_floor_height
                    floor_area = building_width * building_length

                    if floor_area > total_floor_area:
                        # Adjust the footprint to meet the FAR requirement
                        scaling_factor = (total_floor_area / floor_area) ** 0.5
                        building_width *= scaling_factor
                        building_length *= scaling_factor
                        floor_area = building_width * building_length

                    rs.AddBox([(x + (lot_width - building_width) / 2, y + front_yard, current_height),
                               (x + (lot_width + building_width) / 2, y + front_yard, current_height),
                               (x + (lot_width + building_width) / 2, y + front_yard + building_length, current_height),
                               (x + (lot_width - building_width) / 2, y + front_yard + building_length, current_height),
                               (x + (lot_width - building_width) / 2, y + front_yard, current_height + floor_height),
                               (x + (lot_width + building_width) / 2, y + front_yard, current_height + floor_height),
                               (x + (lot_width + building_width) / 2, y + front_yard + building_length, current_height + floor_height),
                               (x + (lot_width - building_width) / 2, y + front_yard + building_length, current_height + floor_height)])
                    
                    current_height += floor_height
    
# Run the script
create_buildings()
