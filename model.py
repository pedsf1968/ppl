import argparse
import json
import math
# import matplotlib as mil
# mil.use('TkAgg')
from collections import defaultdict

import matplotlib.pyplot as plt

class Agent:

    def say_hello(self, first_name):
        return "Bien le bonjour " + first_name + " !"

    def __init__(self, position, **agent_attributes):
        self.position = position
        for attr_name, attr_value in agent_attributes.items():
            setattr(self, attr_name, attr_value)

class Position:

    def __init__(self, longitude_degrees, latitude_degrees):
        # We store the degree values, but we will be mostly using radians
        # because they are much more convenient for computation purposes.

        # return exception if bad values
        assert -180 <= longitude_degrees <= 180
        self.longitude_degrees = longitude_degrees

        assert -90 <= latitude_degrees <= 90
        self.latitude_degrees = latitude_degrees

    # return longitude in radian
    @property
    def longitude(self):
        return self.longitude_degrees * math.pi /180

    # return latitude in radian
    @property
    def latitude(self):
        return self.latitude_degrees * math.pi /180

class Zone:
    """
       A rectangular geographic area bounded by two corners. The corners can
       be top-left and bottom right, or top-right and bottom-left so you should be
       careful when computing the distances between them.
       """

    ZONES = []
    # The width and height of the zones that will be added to ZONES. Here, we
    # choose square zones but we could just as well use rectangular shapes.

    MIN_LONGITUDE_DEGREES = -180
    MAX_LONGITUDE_DEGREES = 180
    MIN_LATITUDE_DEGREES = -90
    MAX_LATITUDE_DEGREES = 90
    WIDTH_DEGREES = 1   # longitude step
    HEIGHT_DEGREES = 1  # latitude step
    EARTH_RADIUS_KILOMETERS = 6371

    def __init__(self, corner1, corner2):
        self.corner1 = corner1
        self.corner2 = corner2
        self.inhabitants = []

    @property
    def population(self):
        """ Get zone population
        :return:
        """
        return len(self.inhabitants)

    @property
    def width(self):
        """ Compute the width of the zone
        :return: the width in kilometer
        """
        return abs((self.corner1.longitude - self.corner2.longitude) * self.EARTH_RADIUS_KILOMETERS)

    @property
    def heigth(self):
        """ Compute the height of the zone
        :return: the height in kilometer
        """
        return abs((self.corner1.latitude - self.corner2.latitude) * self.EARTH_RADIUS_KILOMETERS)

    def add_inhabitant(self, inhabitant):
        """ Add inhabitant in zone
        :param inhabitant: inhabitant to add to the Zone
        :return:
        """
        self.inhabitants.append(inhabitant)

    @property
    def area(self):
        """ Compute the area of the zone
        :return: the area in swuare kilometers
        """
        return self.width * self.heigth

    def population_density(self):
        """ Compute the density of the zone
        :return: the population density of the zone in (people/km2)
        """
        return self.population / self.area

    def average_agreeableness(self):
        """ Compute the average of the agreeableness of the population in the zone
        :return: the agreeableness average
        """
        if not self.inhabitants:
            return 0
        return sum([inhabitant.agreeableness for inhabitant in self.inhabitants]) / self.population

    def population_age(self):
        return self.age

    def contains(self, position):
        """ Determine if the people is in the zone
        :param position: the people position
        :return: true if the position is in the zone
        """
        return position.longitude >= min(self.corner1.longitude, self.corner2.longitude) and \
               position.longitude < max(self.corner1.longitude, self.corner2.longitude) and \
               position.latitude >= min(self.corner1.latitude, self.corner2.latitude) and \
               position.latitude < max(self.corner1.latitude, self.corner2.latitude)

    @classmethod
    def __initialize_zone(cls):
        """ Initialise the zone list
        :return:
        """
        for latitude in range( cls.MIN_LATITUDE_DEGREES, cls.MAX_LATITUDE_DEGREES, cls.HEIGHT_DEGREES):
            for longitude in range(cls.MIN_LONGITUDE_DEGREES, cls.MAX_LONGITUDE_DEGREES, cls.WIDTH_DEGREES):
                bottom_left_corner = Position(longitude, latitude)
                top_right_corner = Position(longitude+ cls.WIDTH_DEGREES, latitude + cls.HEIGHT_DEGREES)
                zone = Zone(bottom_left_corner, top_right_corner)
                cls.ZONES.append(zone)
        print(len(cls.ZONES))

    @classmethod
    def find_zone_that_contains(cls, position):
        if not cls.ZONES:
            # Initialize if needed
            cls.__initialize_zone()

        # Compute the index in the ZONES array that contains the given position
        longitude_index = int((position.longitude_degrees - cls.MIN_LONGITUDE_DEGREES) / cls.WIDTH_DEGREES)
        latitude_index = int((position.latitude_degrees - cls.MIN_LATITUDE_DEGREES) / cls.HEIGHT_DEGREES)
        longitude_bins = int(
            (cls.MAX_LONGITUDE_DEGREES - cls.MIN_LONGITUDE_DEGREES) / cls.WIDTH_DEGREES)  # 180-(-180) / 1
        zone_index = latitude_index * longitude_bins + longitude_index

        # Just checking that the index is correct
        zone = cls.ZONES[zone_index]
        assert zone.contains(position)

        return zone

class BaseGraph:

    def __init__(self):
        self.title = "Your graph title"
        self.x_label = "X-axis label"
        self.y_label = "Y-axis label"

        self.show_grid = True

    def show(self, zones):
        x_values, y_values = self.xy_values(zones)
        self.plot(x_values, y_values)

        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title)
        plt.grid(self.show_grid)
        plt.show()

    def plot(self, x_values, y_values):
        """ Draw defaul point graph. Override this method to do other graph
        :param x_values: list of abscissa values
        :param y_values: list of ordinate values
        :return: display graph
        """
        plt.plot(x_values, y_values, '.')

    def xy_values(self, zones):
        """ Compute values for the graph
        :param zones: list of zones
        :return: X,Y values
        """
        raise NotImplementedError

class AgreeablenessGraph(BaseGraph):

    def __init__(self):
        super().__init__()
        self.title = "Nice people live in the countryside"
        self.x_label = "Population density"
        self.y_label = "Agreeableness"

    def xy_values(self, zones):
        x_values = [zone.population_density() for zone in zones]
        y_values = [zone.average_agreeableness() for zone in zones]
        return x_values, y_values

class IncomeGraph(BaseGraph):

    def __init__(self):
        super().__init__()
        self.title = "People incomes by age"
        self.x_label = "Age"
        self.y_label = "Income"

    def xy_values(self, zones):
        income_by_age = defaultdict(float)
        population_by_age = defaultdict(int)
        for zone in zones:
            for inhabitant in zone.inhabitants:
                income_by_age[inhabitant.age] += inhabitant.income
                population_by_age[inhabitant.age] += 1

        x_values = range(0, 100)
        y_values = [income_by_age[age] / (population_by_age[age] or 1) for age in range(0, 100)]
        return x_values, y_values

def main():
    # Set file name in parameters
    parser = argparse.ArgumentParser("Display population stats")
    parser.add_argument("src", help="Path to source json agents file")
    args = parser.parse_args()

    for agent_attributes in json.load(open(args.src)):
        longitude = agent_attributes.pop('longitude')
        latitude = agent_attributes.pop('latitude')
        # Store agent position
        position = Position(longitude, latitude)

        agent = Agent(position, **agent_attributes)
        zone = Zone.find_zone_that_contains(position)
        zone.add_inhabitant(agent)

    # Graph initialization
    agreeableness_graph = AgreeablenessGraph()
    # Display graph
    agreeableness_graph.show(Zone.ZONES)

    income_graph = IncomeGraph()
    income_graph.show(Zone.ZONES)

if __name__ == "__main__":
    main()