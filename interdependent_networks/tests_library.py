__author__ = 'ivana'
import random
#import interdependent_networks.seismic_data.seismic_data_processor as sdp
import seismic_data.seismic_data_processor as sdp
from interdependent_network_library import *
#import interdependent_networks.seismic_data.image_process as ip
import seismic_data.image_process as ip
#import interdependent_networks.map_handler as mp
import map_handler as mp

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


def soil_value(vs30):
    return 0.322


def seismic_attacks(interdependent_network, x_coordinate, y_coordinate, ndep, version, model, seismic_data_file,
                    max_radius_km=400, centers=None, exp=2.5):

    # get physical network
    physical_net = interdependent_network.get_phys()
    # get vss30
    vs30_matrix = ip.create_values_matrix('seismic_data/m_full_map.png', 'seismic_data/map_scale2.png', 2200, 0)
    # make map
    map_obj = mp.SoilMap(vs30_matrix, soil_value, (x_coordinate, y_coordinate))
    # set soil things onto physical network
    physical_net = map_obj.assign_soil_to_points(physical_net)
    # re-set modified physical network
    interdependent_network.set_physical(physical_net)

    max_radius = km_to_coordinates_chile(max_radius_km)
    seismic_data = load_seismic_data_from_file(seismic_data_file)

    if not centers:
        x_coordinate = int(x_coordinate)
        y_coordinate = int(y_coordinate)
        centers = uniform_centers_for_geography(x_coordinate, y_coordinate, 100)

    contents = []
    for seismic_event in seismic_data:
        print("SEISMIC EVENT: {}".format(seismic_event['id']))
        for center in centers:
            x = center["x"]
            y = center["y"]
            result_dict = probabilistic_localized_attack(interdependent_network, x, y, max_radius,
                                           seismic_probability_function_chile,
                                           seismic_event)
            contents.append(result_dict)

    file_name = csv_title_generator("result", x_coordinate, y_coordinate, exp, n_dependence=ndep,
                                    attack_type="seismic", version=version, model=model)
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "test_results")
    path = os.path.join(path, "seismic")
    save_as_csv(path, file_name, contents)


def load_seismic_data_from_file(seismic_data_file):
    data_dict = sdp.load_from_csv(seismic_data_file)
    seismic_data_list = []
    for event_id in data_dict.keys():
        event = data_dict[event_id][0]
        seismic_event = {"magnitude": event['Magnitude'],
                         "depth": event['Depth'],
                         "event_type": event['Fault Type'],
                         "id": event_id}
        seismic_data_list.append(seismic_event)
    return seismic_data_list


def probabilistic_localized_attack(interdependent_network, x_center, y_center, max_radius, probability_function, param):
    # probability function determines whether a node is removed or not given the conditions
    # param contains other necessary info for the probability_function to work
    physical_network = interdependent_network.get_phys()
    phys_suppliers = interdependent_network.get_phys_providers()
    logic_network = interdependent_network.get_as()
    logic_suppliers = interdependent_network.get_as_providers()
    interdep_graph = interdependent_network.get_interd()
    param["epicenter"] = {"x": x_center, "y": y_center}

    # Get nodes to attack
    nodes_to_attack = []  # name list

    for vertex in physical_network.vs:
        x = vertex["x_coordinate"]
        y = vertex["y_coordinate"]

        # if within maximum radius
        if ((x - x_center) ** 2) + ((y - y_center) ** 2) <= max_radius ** 2:
            # call probability function to know whether to remove the node or not
            if probability_function(vertex, param):
                nodes_to_attack.append(vertex["name"])
    # Create copy from original - why tho?
    graph_copy = InterdependentGraph()
    graph_copy.create_from_graph(logic_network, logic_suppliers, physical_network, phys_suppliers, interdep_graph)

    # attack:
    graph_copy.attack_nodes(nodes_to_attack)
    g_l = graph_copy.get_ratio_of_funtional_nodes_in_AS_network()
    aux_str = "["
    for n in nodes_to_attack:
        aux_str += "{}.".format(n)
    aux_str = aux_str[0:(len(aux_str) - 1)] + "]"

    result_dict = {"x_center": x_center,
                   "y_center": y_center,
                   "GL": g_l,
                   "radius": max_radius,
                   "magnitude": param["magnitude"],
                   "depth": param["depth"],
                   "event_type": param["event_type"],
                   "nodes_removed": aux_str}
    return result_dict


def seismic_probability_function_chile(vertex, params):
    vertex_x = vertex["x_coordinate"]
    vertex_y = vertex["y_coordinate"]
    epicenter_x = params["epicenter"]["x"]
    epicenter_y = params["epicenter"]["y"]
    R_c = numpy.sqrt(((vertex_x - epicenter_x) ** 2) + ((vertex_y - epicenter_y) ** 2))
    R = coordinates_to_km_chile(R_c)
    St_t = vertex["soil"]
    Vs30 = vertex["vs30"]
    Mw = params["magnitude"]
    H = params["depth"]
    Feve = params["event_type"]


    pga_value = get_chile_pga(Mw,H,Feve, R, St_t, Vs30) #(Mw, H, Feve, R, St_t, Vs30)

    # Usar SHINDO scale para las probabilidades
    # notar que la escala no va a ser lineal
    failure_probability = shindo_scale_probability(pga_value)

    return random.uniform(0, 1) <= failure_probability


def shindo_scale_probability(pga):
    gravity_acceleration = 9.8
    ms_pga = pga * gravity_acceleration
    tiers = {#"0": (0, 0.008),
             #"1": (0.008, 0.025),
             #"2": (0.025, 0.08),
             #"3": (0.08,0.25),
             "4": [(0.025, 0.80), (0.01, 0.1)], # delta = 0.55 -> 0.8 m/s => 10% damage probability
             "5-": [(0.8, 1.4),(0.1,0.2)], # delta = 0.6 -> 1.4 m/s => 20% damage probability
             "5+": [(1.4, 2.5),(0.2,0.5)], # delta = 1.1 -> 2.5 m/s => 50% damage probability
             "6-": [(2.5, 3.15),(0.5,0.85)], # delta = 0.65 -> 3.15 m/s => 85% damage probability
             "6+": [(3.15, 4),(0.85,1)], #delta = 0.85 -> 4 m/s => 100% damage probability
             "7": [(4, float('inf')),(1,1)]}

    for tier_number in tiers:
        if tiers[tier_number][0][0] <= ms_pga < tiers[tier_number][0][1]:
            point_1 = (tiers[tier_number][0][0],tiers[tier_number][1][0])
            point_2 = (tiers[tier_number][0][1],tiers[tier_number][1][1])
            prob_value = two_point_line_eq(ms_pga, point_1, point_2)
            return prob_value
    return 0


def two_point_line_eq(x, point_1, point_2):
    x1 = point_1[0]
    y1 = point_1[1]
    x2 = point_2[0]
    y2 = point_2[1]
    return (y2 - y1) * ((x - x1)/(x2 - x1)) + y1


def get_chile_pga(Mw, H, Feve, R, St_t, Vs30):
    c1 = -2.8548
    c2 = 0.7741
    c3 = -0.97558
    c4 = 0.1
    c5 = -0.00174
    c6 = 5
    c7 = 0.35
    c8 = 0.00586
    c9 = -0.03958
    delta_c1 = 2.5699
    delta_c2 = -0.4761
    delta_c3 = -0.52745
    h0 = 50  # 50 km
    Mr = 5
    Vref = 1530  # 1530 m/s

    if Feve == 0:
        delta_fm = c9 * (Mw ** 2)
    else:
        delta_fm = delta_c1 + delta_c2 * Mw

    Ff = c1 + c2*Mw + c8*(H - h0)*Feve + delta_fm

    g = (c3 + c4*(Mw - Mr) + delta_c3*Feve)
    R0 = ((1 - Feve)*c6 * 10**(c7*(Mw - Mr)))

    Fd = g*numpy.log10(R + R0) + c5*R

    Fs = St_t*numpy.log10((Vs30+0.00000000000001)/Vref)

    log10_pga = Ff + Fd + Fs

    pga = 10 ** log10_pga
    return pga


def coordinates_to_km_chile(coordinates):
    coordinate = 20
    kms = 175
    factor = kms/coordinate # kms per unit of "coordinate"
    return coordinates*factor


def km_to_coordinates_chile(kms):
    coordinate = 20
    km = 175
    factor = coordinate / km  # "coordinate" per km
    return kms * factor
