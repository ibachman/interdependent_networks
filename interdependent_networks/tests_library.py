__author__ = 'ivana'
import random
from interdependent_network_library import *
# from interdependent_networks.interdependent_network_library import *
#
import numpy
import datetime


def single_network_attack(interdependent_network, network_to_attack, file_name, iter_number, process_name=""):
    print(" -> Results path: {}".format(file_name))
    physical_network = interdependent_network.get_phys()
    phys_suppliers = interdependent_network.get_phys_providers()
    logic_network = interdependent_network.get_as()
    logic_suppliers = interdependent_network.get_as_providers()
    interdep_graph = interdependent_network.get_interd()

    if not network_to_attack == "logic" and not network_to_attack == "physical":
        print("Choose a valid network to attack")
        return
    n_phys = len(physical_network.vs)
    n_logic = len(logic_network.vs)
    if network_to_attack == "logic":
        samp = logic_network.vs["name"]
        iteration_range = n_logic
    else:
        samp = physical_network.vs["name"]
        iteration_range = n_phys

    iteration_results = []
    for j in range(1, n_phys + n_logic):
        iteration_results.append([])
    for j in range(iter_number):
        print(" ----------[[" + str(datetime.datetime.now())+ "]]--" + process_name + " -- iteration: " + str(j+1))
        for i in range(1, iteration_range):
            graph_copy = InterdependentGraph()
            graph_copy.create_from_graph(logic_network,logic_suppliers,physical_network,phys_suppliers,interdep_graph)
            list_of_nodes_to_attack = random.sample(samp, i)

            graph_copy.attack_nodes(list_of_nodes_to_attack)
            iteration_results[(i-1)].append(graph_copy.get_ratio_of_funtional_nodes_in_AS_network())
    
    print("Staring to write results " + str(datetime.datetime.now()))

    with open(file_name,'w') as csvfile:
        print(" -> Writing results on: {}".format(file_name))
        fieldnames = ["1-p", "mean", "std"]
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for i in range(iteration_range-1):
            writer.writerow({'1-p': ((i+1)*1.0)/iteration_range,
                             'mean': numpy.mean(iteration_results[i]),
                             'std': numpy.std(iteration_results[i])})


# this method calculates 100 iteration of attacks over the whole system
def whole_system_attack(interdependent_network, file_name, iter_number):
    physical_network = interdependent_network.get_phys()
    phys_suppliers = interdependent_network.get_phys_providers()
    logic_network = interdependent_network.get_as()
    logic_suppliers = interdependent_network.get_as_providers()
    interdep_graph = interdependent_network.get_interd()
    n_phys = len(physical_network.vs)
    n_logic = len(logic_network.vs)
    iteration_results = []
    for j in range(1,n_phys+n_logic):
        iteration_results.append([])
    for j in range(iter_number):
        for i in range(1,n_phys+n_logic):
            graph_copy = InterdependentGraph()
            graph_copy.create_from_graph(logic_network,logic_suppliers,physical_network,phys_suppliers,interdep_graph)
            list_of_nodes_to_attack = random.sample(physical_network.vs["name"]+logic_network.vs["name"], i)
            graph_copy.attack_nodes(list_of_nodes_to_attack)
            iteration_results[(i-1)].append(graph_copy.get_ratio_of_funtional_nodes_in_AS_network())
    with open(file_name,'w') as csvfile:
        fieldnames = ["1-p","mean","std"]
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for i in range(n_phys+n_logic-1):
            writer.writerow({'1-p':(i+1)*1.0/(n_logic+n_phys),'mean':numpy.mean(iteration_results[i]),'std':numpy.std(iteration_results[i])})


def mtfr_mean_and_std(graph_list, file_name):
    mtfr_list = []
    for interdependent_system in graph_list:
        mtfr_list.append(interdependent_system.node_mtfr())
    with open(file_name,'w') as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=mtfr_list)
        writer.writeheader()


def single_localized_attack(interdependent_network, x_coordinate,
                     y_coordinate, x_center=-1, y_center=-1, radius=-1,
                     max_radius=-1, center_function=None, radius_function=None, exp="2.5", version="0", file=None):
    physical_network = interdependent_network.get_phys()
    phys_suppliers = interdependent_network.get_phys_providers()
    logic_network = interdependent_network.get_as()
    logic_suppliers = interdependent_network.get_as_providers()
    interdep_graph = interdependent_network.get_interd()

    if center_function:
        x_center, y_center = center_function(physical_network, max_radius, x_coordinate, y_coordinate)
    if radius_function:
        radius = radius_function(physical_network, max_radius, x_coordinate, y_coordinate)
    if x_center < 0 or y_center < 0 or radius < 0:
        exit("Localized attacks: negative center and/or raidus")

    # Create copy from original - why tho?
    graph_copy = InterdependentGraph()
    graph_copy.create_from_graph(logic_network, logic_suppliers, physical_network, phys_suppliers, interdep_graph)

    # Get nodes to attack
    nodes_to_attack = []  # name list
    for vertex in physical_network.vs:
        x = vertex["x_coordinate"]
        y = vertex["y_coordinate"]
        if ((x - x_center) ** 2) + ((y - y_center) ** 2) <= radius ** 2:
            nodes_to_attack.append(vertex["name"])

    # attack:
    graph_copy.attack_nodes(nodes_to_attack)
    g_l = graph_copy.get_ratio_of_funtional_nodes_in_AS_network()
    aux_str = "["
    for n in nodes_to_attack:
        aux_str += "{}.".format(n)
    aux_str = aux_str[0:(len(aux_str)-1)] + "]"

    result_dict = {"x_center": x_center,
                   "y_center": y_center,
                   "nodes_removed": aux_str,
                   "GL": g_l,
                   "radius": radius}
    return result_dict


def localized_attack(iterations, interdependent_network, x_coordinate,
                     y_coordinate, radius, ndep, providers, version, model, strategy='', center_file=None, centers=None,
                     max_radius=-1, center_function=None, radius_function=None, exp="2.5", file=None):

    if not centers:
        centers = []
        if center_file:
            # get centers from file
            with open(center_file, "r") as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar=',')
                for row in reader:
                    centers.append({"x": row[0], "y": row[1]})
        else:
            x_coordinate = int(x_coordinate)
            y_coordinate = int(y_coordinate)
            centers = uniform_centers_for_geography(x_coordinate, y_coordinate, 100)

    contents = []
    for position in centers:
        for r in radius:
            contents.append(single_localized_attack(interdependent_network, x_coordinate, y_coordinate, x_center=position["x"],
                                    y_center=position["y"], radius=r))
    file_name = csv_title_generator("result", x_coordinate, y_coordinate, exp, n_dependence=ndep,
                                    attack_type="localized", version=version, model=model)
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "test_results")
    if strategy != '':
        path = os.path.join(path, strategy)
    save_as_csv(path, file_name, contents)


def simple_radius(graph, radius, length, width):
    return radius


def random_center(graph, max_radius, x_coordinate, y_coordinate):
    x_center = numpy.random.uniform(0, max_radius)
    y_center = numpy.random.uniform(0, max_radius)
    return x_center, y_center


def uniform_centers_for_geography(width, length, amount):
    area = width*length
    square_side = int(numpy.sqrt(area/amount))
    width_cells = int(width/square_side)
    length_cells = int(length/square_side)
    centers = []
    p = 1
    for i in range(width_cells):
        x_center = (i + 0.5)*square_side
        for j in range(length_cells):
            y_center = (j+0.5)*square_side
            centers.append({"x": x_center, "y": y_center})
    return centers
