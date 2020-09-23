__author__ = 'ivana'
import datetime
import network_generators as network_generators
# import interdependent_networks.network_generators as network_generators
import tests_library as tests_library
# import interdependent_networks.tests_library as tests_library
from interdependent_network_library import *
# from interdependent_networks.interdependent_network_library import *
#


def run_test(x_coordinate, y_coordinate, exp, n_inter, n_logic_suppliers,
             version, n_logic, n_phys, iter_number, READ_flag=False, attack_types=[], model=[], logic_flag=False,
             physical_flag=False, phys_iteration=0, strategy='', process_name="", localized_attack_data=[]):
    attack_logic = 'logic' in attack_types
    attack_phys = 'physical' in attack_types
    attack_both = 'both' in attack_types
    attack_localized = 'localized' in attack_types

    if READ_flag:
        print("start {}".format(datetime.datetime.now()))
        network_system = InterdependentGraph()
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, "networks")
        AS_title = os.path.join(path, csv_title_generator("logic", x_coordinate, y_coordinate, exp, version=1))
        phys_title = os.path.join(path, csv_title_generator("physic", x_coordinate, y_coordinate, exp, version=version,
                                                            model=model))
        interd_title = os.path.join(path,csv_title_generator("dependence", x_coordinate, y_coordinate, exp, n_inter, 6,
                                                             version=1))
        providers_title = os.path.join(path, csv_title_generator("providers", x_coordinate, y_coordinate, exp, n_inter,
                                                                 6, version=1))
        nodes_tittle = os.path.join(path,csv_title_generator("nodes",x_coordinate,y_coordinate,exp,version=1))
        network_system.create_from_csv(AS_title, phys_title, interd_title, nodes_tittle, providers_csv=providers_title)
        print("system created {}".format(datetime.datetime.now()))
        sub_dir = 'simple_graphs'

        if strategy != '':
            path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(path, "networks",strategy, csv_title_generator("candidates", x_coordinate, y_coordinate,
                                                                              exp, version=version, model=model))

            edges_to_add = get_list_of_tuples_from_csv(path)
            network_system.add_edges_to_physical_network(edges_to_add)
            sub_dir = strategy

        if attack_phys:
            print("physical test attack " + str(datetime.datetime.now()))
            # attack only physical network
            physical_attack_title = csv_title_generator("result", x_coordinate, y_coordinate, exp, n_dependence=n_inter,
                                        attack_type="physical", version=version, model=model)

            path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(path, "test_results", sub_dir, physical_attack_title)
            tests_library.single_network_attack(network_system, "physical", path, iter_number, process_name=process_name)
        if attack_localized:
            print("localized attack test " + str(datetime.datetime.now()))
            # attack physical network using localized attacks
            radius = localized_attack_data["radius"]
            tests_library.localized_attack(iter_number, network_system, x_coordinate, y_coordinate, radius, n_inter,
                                           n_logic_suppliers, version, model, strategy=strategy)
            print("localized attack test " + str(datetime.datetime.now()))
        else:
            pass

    elif logic_flag:
        # generate AS network
        as_graph = network_generators.generate_logic_network(n_logic, exponent=exp)
        network_system = InterdependentGraph()
        network_system.set_AS(as_graph)
        network_system.save_logic(x_coordinate, y_coordinate, exp, n_inter, version=version)

        print("amount of connected components " + str(len(as_graph.clusters())))
        print("AS ready " + str(datetime.datetime.now()))

    elif physical_flag:
        if phys_iteration == 0:
            x_coord, y_coord = network_generators.generate_coordinates(n_phys, x_coordinate, y_coordinate)
            save_nodes_to_csv(x_coord, y_coord, x_coordinate, y_coordinate, exp, n_inter, n_logic_suppliers,
                              version=version)
        
        else:
            # generate physical network
            coord_title = "networks/" + csv_title_generator("nodes", x_coordinate, y_coordinate, exp, version=version)
            x_coord, y_coord = get_list_of_coordinates_from_csv(coord_title)
            x, y, phys_graph = network_generators.generate_physical_network(n_phys, x_coordinate, y_coordinate, model, x_coord, y_coord)
            network_system = InterdependentGraph()
            network_system.set_physical(phys_graph)
            # Save physical
            network_system.save_physical(x_coordinate, y_coordinate, exp, n_inter, version=phys_iteration, model=model)

        print("phys ready " + str(datetime.datetime.now()))

    else:

        print("start " + str(datetime.datetime.now()))

        phys_id_list = []
        for i in range(n_phys):
            phys_id_list.append('p'+str(i))

        logic_id_list = []
        for i in range(n_logic):
            logic_id_list.append('l'+str(i))

        interdep_graph = network_generators.set_interdependencies(phys_id_list, logic_id_list, n_inter)

        print("interdep ready "+ str(datetime.datetime.now()))

        as_suppliers = network_generators.set_logic_suppliers(logic_id_list, n_logic_suppliers, n_inter, interdep_graph)

        print("AS suppliers ready "+ str(datetime.datetime.now()))

        phys_suppliers = network_generators.set_physical_suppliers(interdep_graph, as_suppliers)

        print("Phys suppliers ready "+ str(datetime.datetime.now()))

        network_system = InterdependentGraph()
        network_system.create_from_empty_logic_physical(logic_id_list,as_suppliers,phys_id_list,phys_suppliers,interdep_graph)

        print("system created "+ str(datetime.datetime.now()))

        network_system.save_to_pdf(x_coordinate,y_coordinate,exp,n_inter,version=version)

        print("system saved "+ str(datetime.datetime.now()))
    print("run test done")


def add_edges(x_coordinate, y_coordinate, exp, n_inter, n_logic_suppliers, version, n_logic, n_phys, iter_number,
              model=[], phys_iteration=0, strategy='random,degree,distance,external'):
    path = os.path.dirname(os.path.abspath(__file__))
    print("Creando arcos")
    add_random = 'random' in strategy
    add_degree = 'degree' in strategy
    add_distance = 'distance' in strategy
    add_external = 'external' in strategy
    # Read current edges
    title = os.path.join(path,"networks",csv_title_generator("physic", x_coordinate, y_coordinate, exp, version=phys_iteration, model=model))
    phys_graph = set_graph_from_csv(title)

    # Read coordinates
    print(version)
    coord_title = os.path.join(path,"networks", csv_title_generator("nodes", x_coordinate, y_coordinate, exp, version=version))
    print("Leyendo nodos")
    x_coord, y_coord = get_list_of_coordinates_from_csv(coord_title)
    print("Lei nodos")

    number_of_edges_to_add = 640
    
    if add_random:
        new_edges = network_generators.generate_edges_to_add_random(number_of_edges_to_add, phys_graph)
        network_generators.save_edges_to_csv(new_edges, x_coordinate, y_coordinate, exp, version=phys_iteration, model=model,
                                             strategy="random")
    
    if add_degree:
        percentage = 97
        new_edges = network_generators.generate_edges_to_add_degree(phys_graph, percentage, number_of_edges_to_add)
        network_generators.save_edges_to_csv(new_edges, x_coordinate, y_coordinate, exp, version=phys_iteration, model=model,
                                             strategy="degree")

    if add_distance:
        percentage = 97
        new_edges = network_generators.generate_edges_to_add_distance(phys_graph, x_coord, y_coord, percentage,
                                                                      number_of_edges_to_add)
        network_generators.save_edges_to_csv(new_edges, x_coordinate, y_coordinate, exp, version=phys_iteration, model=model,
                                             strategy="distance")

    if add_external:
        dependence_tittle = "networks/" + csv_title_generator("dependence", x_coordinate, y_coordinate, exp, n_inter, 6,
                                                              version=version)
        dep_graph = set_graph_from_csv(dependence_tittle)
        percentage = 10 #TODO
        new_edges = network_generators.genererate_edges_by_degree(phys_graph, x_coord, y_coord, percentage,
                                                                  number_of_edges_to_add, external=True,
                                                                  dependence_graph=dep_graph)
        network_generators.save_edges_to_csv(new_edges, x_coordinate, y_coordinate, exp, version=phys_iteration, model=model,
                                             strategy="external")
    print("Arcos creados")


def distributions(x_coordinate, y_coordinate, exp, model):
    dist = {}
    for i in range(1, 11):
        title = "networks/" + csv_title_generator("physic", x_coordinate, y_coordinate, exp, version=str(i), model=model)
        phys_graph = set_graph_from_csv(title)
        for vertex in phys_graph.vs:
            degree = vertex.degree()
            if degree not in dist:
                dist[degree] = 1
            else:
                dist[degree] += 1
    return dist


