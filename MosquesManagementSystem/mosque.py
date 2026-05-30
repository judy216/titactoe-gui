class Mosque:
    """Represents a single mosque entry."""

    def __init__(self, mosque_id, name, mosque_type, address, coordinates, imam_name):
        self.mosque_id = mosque_id
        self.name = name
        self.mosque_type = mosque_type
        self.address = address
        self.coordinates = coordinates
        self.imam_name = imam_name

    def __str__(self):
        return (
            f"ID: {self.mosque_id}  |  Name: {self.name}  |  Type: {self.mosque_type}  |  "
            f"Address: {self.address}  |  Coordinates: {self.coordinates}  |  Imam: {self.imam_name}"
        )
