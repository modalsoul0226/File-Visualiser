"""Assignment 2: Modelling Population Data

=== CSC148 Fall 2016 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains a new class, PopulationTree, which is used to model
population data drawn from the World Bank API.
Even though this data has a fixed hierarchichal structure (only three levels:
world, region, and country), because we are able to model it using an
AbstractTree subclass, we can then run it through our treemap visualisation
tool to get a nice interactive graphical representation of this data.

NOTE: You'll need an Internet connection to access the World Bank API
to get started working on this assignment.

Recommended steps:
1. Read through all docstrings in this files once. There's a lot to take in,
   so don't feel like you need to understand it all the first time.
   It may be helpful to draw a small diagram of how all the helper functions
   fit together - we've provided most of the structure for you already.
2. Complete the helpers _get_population_data and _get_region_data.
   Both of these can be completed without recursion or any use of trees
   at all: they are simply exercises in taking some complex JSON data,
   and extracting the necessary information from them.
3. Review the PopulationTree constructor docstring. Note that when the first
   parameter is set to False, this behaves exactly the same as the
   AbstractTree constructor.
4. Complete _load_data. Use the PopulationTree constructor, but you should
   only need to pass in False for the first argument (this allows you to
   create the region and country nodes directly, without trying to access
   the World Bank API again).
"""
import json
import urllib.request as request

from tree_data import AbstractTree


# Constants for the World Bank API urls.
STAR_WARS_PLANETS = 'http://swapi.co/api/planets/1/?format=wookie'
WORLD_BANK_BASE = 'http://api.worldbank.org/countries'
WORLD_BANK_POPULATIONS = (
    WORLD_BANK_BASE +
    '/all/indicators/SP.POP.TOTL?format=json&date=2014:2014&per_page=270'
)
WORLD_BANK_REGIONS = (
    WORLD_BANK_BASE + '?format=json&date=2014:2014&per_page=310'
)


class PopulationTree(AbstractTree):
    """A tree representation of country population data.

    This tree always has three levels:
      - The root represents the entire world.
      - Each node in the second level is a region (defined by the World Bank).
      - Each node in the third level is a country.

    The data_size attribute corresponds to the 2014 population of the country,
    as reported by the World Bank.

    See https://datahelpdesk.worldbank.org/ for details about this API.
    """
    def __init__(self, world, root=None, subtrees=None, data_size=0):
        """Initialize a new PopulationTree.

        If <world> is True, then this tree is the root of the population tree,
        and it should load data from the World Bank API.
        In this case, none of the other parameters are used.

        If <world> is False, pass the other arguments directly to the superclass
        constructor. Do NOT load new data from the World Bank API.

        @type self: PopulationTree
        @type world: bool
        @type root: object
        @type subtrees: list[PopulationTree] | None
        @type data_size: int
        """
        if world:
            region_trees = _load_data()
            AbstractTree.__init__(self, 'World', region_trees)
        else:
            if subtrees is None:
                subtrees = []
            AbstractTree.__init__(self, root, subtrees, data_size)

    def get_separator(self):
        """Return the string used to represent the path of World ->
        Region -> Country.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        self._root always has a value i.e. not an empty tree.

        @type self: PopulationTree
        @rtype: str
        """
        if self._parent_tree:
            return self._parent_tree.get_separator() + '\\' + self._root
        else:
            return self._root


def _load_data():
    """Create a list of trees corresponding to different world regions.

    Each tree consists of a root node -- the region -- attached to one or
    more leaves -- the countries in that region.

    @rtype: list[PopulationTree]
    """
    # Get data from World Bank API.
    country_populations = _get_population_data()
    regions = _get_region_data()
    # Each region tree has only two levels:
    #   - a root storing the name of the region
    #   - zero or more leaves, each representing a country in the region
    leaf_dict = dict()
    result = list()
    # Construct a leaf dictionary with its keys being the name of the country,
    # and values being the PopulationTree accordingly.
    for country in country_populations:
        leaf_dict[country] = PopulationTree(False, root=country,
                                            data_size=country_populations
                                            [country])
    # Iterate through each region.
    for region in regions:
        subtrees = list()
        # Iterate all the countries in a given region.
        for country in regions[region]:
            # Add each country to the region's subtree list.
            if country in leaf_dict:
                subtrees.append(leaf_dict[country])
        # Add each region to the world's subtree list.
        result.append(PopulationTree(False, root=region, subtrees=subtrees))
    return result


def _get_population_data():
    """Return country population data from the World Bank.

    The return value is a dictionary, where the keys are country names,
    and the values are the corresponding populations of those countries.

    Ignore all countries that do not have any population data,
    or population data that cannot be read as an int.

    @rtype: dict[str, int]
    """
    # The first element returned is ignored because it's just metadata.
    # The second element's first 47 elements are ignored because they aren't
    # countries.
    _, population_data = _get_json_data(WORLD_BANK_POPULATIONS)
    population_data = population_data[47:]
    countries = {}
    # Iterate through every country's data.
    for data in population_data:
        country = data['country']['value']
        population = data['value']
        try:
            # Ignore countries that have no population data.
            if population:
                countries[country] = int(population)
        # Ignore countries whose population data cannot be read as an int.
        except ValueError:
            continue
    return countries


def _get_region_data():
    """Return country region data from the World Bank.

    The return value is a dictionary, where the keys are region names,
    and the values a list of country names contained in that region.

    Ignore all regions that do not contain any countries.

    @rtype: dict[str, list[str]]
    """
    # We ignore the first component of the returned JSON, which is metadata.
    _, country_data = _get_json_data(WORLD_BANK_REGIONS)
    regions = {}
    # Iterate through every region's data.
    for data in country_data:
        country = data['name']
        region = data['region']['value']
        # Ignore regions that have no countries and those with 'Aggregates' as
        # their values.
        if country and region != 'Aggregates':
            # If region already exists as a key in the dictionary, update
            # its value. Otherwise, create a new set of key-value in
            # the dictionary.
            if region in regions:
                regions[region].append(country)
            else:
                regions[region] = [country]
    return regions


def _get_json_data(url):
    """Return a dictionary representing the JSON response from the given url.

    You should not modify this function.

    @type url: str
    @rtype: Dict
    """
    response = request.urlopen(url)
    return json.loads(response.read().decode())


if __name__ == '__main__':
    import python_ta

    # print(_get_json_data(STAR_WARS_PLANETS))

    python_ta.check_errors(config='pylintrc.txt')
    python_ta.check_all(config='pylintrc.txt')
