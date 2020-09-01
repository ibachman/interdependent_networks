__author__ = 'ivana'
import datetime
import network_generators
import tests_library
from interdependent_network_library import *


def run_test(x_coordinate, y_coordinate, exp, n_inter, n_logic_suppliers,
             version, n_logic, n_phys, iter_number, READ_flag=False, attack_types=[], model=[], logic_flag=False,
             physical_flag=False, phys_iteration=0, strategy='', process_name=""):
    attack_logic = 'logic' in attack_types
    attack_phys = 'physical' in attack_types
    attack_both = 'both' in attack_types

    if READ_flag:
        print("start "+ str(datetime.datetime.now()))

        network_system = InterdependentGraph()
        AS_title = "networks/"+csv_title_generator("logic", x_coordinate, y_coordinate, exp, version=1)
        phys_title = "networks/"+csv_title_generator("physic", x_coordinate, y_coordinate, exp, version=version,
                                                     model=model)
        interd_title = "networks/"+csv_title_generator("dependence", x_coordinate, y_coordinate, exp, n_inter, 6,
                                                       version=1)
        providers_title = "networks/"+csv_title_generator("providers", x_coordinate, y_coordinate, exp, n_inter, 6,
                                                          version=1)
        nodes_tittle = "networks/"+csv_title_generator("nodes",x_coordinate,y_coordinate,exp,version=1)

        network_system.create_from_csv(AS_title,phys_title,interd_title,nodes_tittle,providers_csv=providers_title)
        print("system created "+ str(datetime.datetime.now()))
        #curr_edges = len(network_system.physical_network.get_edgelist())
        #number_of_edges_to_add = (curr_edges + 9999) / 4 - curr_edges
        #new_edges = network_gen.generate_edges_to_add(number_of_edges_to_add,network_system.physical_network)
        #network_gen.save_edges_to_csv(new_edges,x_coordinate,y_coordinate,exp,n_inter,n_logic_suppliers,version=version)
        sub_dir = 'simple_graphs'

        if strategy != '':
            candidates_title = "networks/"+ strategy +"/"+csv_title_generator("candidates",x_coordinate,y_coordinate,exp,version=version, model=model)
            edges_to_add = get_list_of_tuples_from_csv(candidates_title)
            network_system.add_edges_to_physical_network(edges_to_add)
            sub_dir = strategy

        if attack_phys:
            print("physical test attack "+ str(datetime.datetime.now()))
            # attack only physical network
            physical_attack_title = "result"+ "_" + str(x_coordinate) + "x" + str(y_coordinate) + "_exp_" + str(
                exp) + "_ndep_" + str(n_inter) + "_att_physical"

            if version is not "":
                physical_attack_title = physical_attack_title + "_v" + str(version)
            if model is not "":
                physical_attack_title = physical_attack_title + "_m_" + str(model) + ".csv"
            tests_library.single_network_attack(network_system, "physical", "test_results/" + sub_dir +"/" +
                                                physical_attack_title, iter_number, process_name=process_name)

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
            x, y ,phys_graph = network_generators.generate_physical_network(n_phys, x_coordinate, y_coordinate, model, x_coord, y_coord)
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



    """if n_inter==1:
            number_of_edges_to_add = (curr_edges + 9999) / 4 - curr_edges
            #print number_of_edges_to_add
            new_edges = network_gen.generate_edges_to_add(number_of_edges_to_add,phys_graph)
            network_gen.save_edges_to_csv(new_edges,x_coordinate,y_coordinate,exp,n_inter,n_logic_suppliers,version=version, model=model) """

    """ ###################### RUN TESTS #############################

    if not os.path.exists('test_results'):
        os.makedirs('test_results')

    if attack_logic:
        # attack only logic network
        print "logic test attack", datetime.datetime.now()

        logic_attack_title = \
            csv_title_generator("result", x_coordinate, y_coordinate, exp, n_inter,
                                n_logic_suppliers, attack_type="logic", version=version, model=model)
        test_gen.single_network_attack(network_system, "logic", "test_results/"+logic_attack_title, iter_number)

    if attack_phys:
        print "physical test attack", datetime.datetime.now()
        # attack only physical network
        if READ_flag:
            physical_attack_title = "result"+ "_" + str(x_coordinate) + "x" + str(y_coordinate) + "_exp_" + str(
                exp) + "_ndep_" + str(n_inter) + "_att_physical" + "_lprovnum_" + str(n_logic_suppliers)
            if version is not "":
                physical_attack_title = physical_attack_title + "_v" + str(version)
            if model is not "":
                physical_attack_title = physical_attack_title + "_m_" + str(model)
            physical_attack_title += "_withextraedges.csv"

        else:
            physical_attack_title = \
                csv_title_generator("result", x_coordinate, y_coordinate, exp, n_inter,
                                    n_logic_suppliers, attack_type="physical", version=version, model=model)
        test_gen.single_network_attack(network_system, "physical", "test_results/"+physical_attack_title, iter_number)

    if attack_both:
        print "whole net test attack", datetime.datetime.now()
        # attack both networks
        simult_attack_title = \
            csv_title_generator("result", x_coordinate, y_coordinate, exp, n_inter,
                                n_logic_suppliers, attack_type="both", version=version, model=model)
        test_gen.whole_system_attack(network_system, "test_results/"+simult_attack_title, iter_number)
    print "---------------- Finished -----------------", datetime.datetime.now() """


def add_edges(x_coordinate, y_coordinate, exp, n_inter, n_logic_suppliers, version, n_logic, n_phys, iter_number,
              model=[], phys_iteration=0, strategy='random,degree,distance,external'):
    print("Creando arcos")
    add_random = 'random' in strategy
    add_degree = 'degree' in strategy
    add_distance = 'distance' in strategy
    add_external = 'external' in strategy
    # Read current edges
    title = "networks/" + csv_title_generator("physic", x_coordinate, y_coordinate, exp, version=phys_iteration, model=model)
    phys_graph = set_graph_from_csv(title)

    # Read coordinates
    coord_title = "networks/"+ csv_title_generator("nodes", x_coordinate, y_coordinate, exp, version=version)
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


