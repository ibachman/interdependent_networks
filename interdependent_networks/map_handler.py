
class SoilMap(object):

    def __init__(self, vs30_matrix, soil_values, space_dimensions):
        self.space_dimensions = space_dimensions
        self.vs30_matrix = vs30_matrix
        self.soil_values = soil_values # -0.32km

    def assign_soil_to_points(self, physical_network):
        space_x = self.space_dimensions[0]
        space_y = self.space_dimensions[1]
        vs30_matrix_y_length = len(self.vs30_matrix)
        y_step = space_y/vs30_matrix_y_length

        for vertex in physical_network.vs:
            x = vertex["x_coordinate"]
            y = vertex["y_coordinate"]
            # find y axis bucket
            y_bucket = int(y//y_step)
            # find x bucket
            x_len = len(self.vs30_matrix[y_bucket])
            x_step = space_x/x_len
            x_bucket = int(x//x_step)
            vs30_value = self.vs30_matrix[y_bucket][x_bucket]
            vertex["vs30"] = vs30_value
            vertex["soil"] = self.soil_values(vs30_value)

        return physical_network

