import overpy

# Define the bounding box coordinates (min_lat, min_lon, max_lat, max_lon)
bounding_box = (50.745, 7.17, 50.75, 7.18)

# Create the Overpass API object
api = overpy.Overpass()

# Construct the Overpass query to retrieve building polygons within the bounding box
query = f"""
    [out:json];
    (
        way["building"]({bounding_box[0]}, {bounding_box[1]},
                        {bounding_box[2]}, {bounding_box[3]});
        relation["building"]({bounding_box[0]}, {bounding_box[1]}, {
    bounding_box[2]}, {bounding_box[3]});
    );
    out geom;
"""

# Perform the query with additional information to resolve missing nodes
result = api.query(query)


# Process the result
for way in result.ways:
    polygon = [(node.lat, node.lon) for node in way.nodes]
    # Process the polygon as needed
    print(f"Building Polygon: {polygon}")


for relation in result.relations:
    for member in relation.members:
        if member.type == 'way':
            polygon = [(node.lat, node.lon) for node in member.way.nodes]
            # Process the polygon as needed
            print(f"Building Polygon: {polygon}")


# Create the Overpass API object
api = overpy.Overpass()

# Construct the Overpass query to retrieve building polygons within the bounding box
query = f"""
    [out:json];
    (
        way["building"]({bounding_box[0]}, {bounding_box[1]},
                        {bounding_box[2]}, {bounding_box[3]});
        relation["building"]({bounding_box[0]}, {bounding_box[1]}, {
    bounding_box[2]}, {bounding_box[3]});
    );
    out geom;
"""

# Perform the query
result = api.query(query)

# Process the result
for way in result.ways:
    polygon = [(node.lat, node.lon) for node in way.nodes]
    # Process the polygon as needed
    print(f"Building Polygon: {polygon}")


"""
for relation in result.relations:
    for member in relation.members:
        if member.type == 'way':
            polygon = [(node.lat, node.lon) for node in member.way.nodes]
            # Process the polygon as needed
            print(f"Building Polygon: {polygon}")
"""
