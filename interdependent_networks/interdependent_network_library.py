import igraph
import csv
import os


def csv_title_generator(graph_type, x_coordinates, y_coordinates, pg_exponent, n_dependence="", l_providers="",
                        attack_type="", version="", model=""):
    title = str(graph_type) + "_" + str(x_coordinates) + "x" + str(y_coordinates) + "_exp_" + str(
        pg_exponent)
    
    if n_dependence is not "":
        title += "_ndep_" + str(n_dependence)
    if attack_type is not "":
        title = title + "_att_" + str(attack_type)
    if l_providers is not "":
        amount_of_logic_providers = str(l_providers)
        title += "_lprovnum_" + str(amount_of_logic_providers)
    if version is not "":
        title = title + "_v" + str(version)
    if model is not "":
        title = title + "_m_" + str(model)

    title += ".csv"
    return title


def set_graph_from_csv(csv_file, graph=None):
    if graph is None:
        rename_map = {}
        k = 0
        names_list = []
        print(csv_file)
        with open(csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar=',')
            edge_list = []
            for row in reader:
                first = row[0]
                second = row[1]
                if first not in rename_map:
                    rename_map[first] = k
                    k += 1
                    names_list.append(first)
                if second not in rename_map:
                    rename_map[second] = k
                    k += 1
                    names_list.append(second)
                edge_list.append((rename_map[first], rename_map[second]))
        number_of_nodes = len(rename_map)
        graph = igraph.Graph()
        graph.add_vertices(number_of_nodes)
        graph.vs['name'] = names_list
        graph.add_edges(edge_list)
    else:
        with open(csv_file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar=',')
            for row in reader:
                first = row[0]
                second = row[1]
                graph.add_edge(first, second)
    return graph


def write_graph_with_node_names(graph, title):
    with open(title, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        lst = graph.get_edgelist()
        names = graph.vs["name"]
        for i in range(len(lst)):
            j = lst[i][0]
            k = lst[i][1]
            writer.writerow([names[j], names[k]])


def get_list_of_tuples_from_csv(csv_file):
    list_of_tuples = []
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar=',')
        for row in reader:
            first = int(row[0])
            second = int(row[1])
            list_of_tuples.append((first, second))
    return list_of_tuples


def save_nodes_to_csv(x_positions, y_positions, x_coordinates, y_coordinates, pg_exponent, n_dependence, l_providers,
                      attack_type="", version="", model=""):
    title = csv_title_generator("nodes", x_coordinates, y_coordinates, pg_exponent,
                                attack_type="", version=version, model=model)
    full_directory = "networks/" + title

    with open(full_directory, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        for i in range(len(x_positions)):
            j = x_positions[i]
            k = y_positions[i]
            writer.writerow([i, j, k])


def get_list_of_coordinates_from_csv(csv_file):
    x_coord = []
    y_coord = []
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar=',')
        for row in reader:
            x_coordinate = float(row[1])
            y_coordinate = float(row[2])
            x_coord.append(x_coordinate)
            y_coord.append(y_coordinate)
    return x_coord, y_coord


def get_nodes_in_radius(physical_network, x_coordinate, y_coordinate, exp, version):

    # Read coordinates
    coord_title = "networks/" + csv_title_generator("nodes", x_coordinate, y_coordinate, exp, version=version)
    x_coord, y_coord = get_list_of_coordinates_from_csv(coord_title)


class InterdependentGraph(object):

    def __init__(self):
        pass

    def save_physical(self, x_coordinates, y_coordinates, pg_exponent, n_dependence, version="", model=""):
        physical_graph = self.physical_network
        if not os.path.exists('networks'):
            os.makedirs('networks')
        # write physical
        physical_name = csv_title_generator("physic", x_coordinates, y_coordinates, pg_exponent, version=version, model=model)
        print("Empezando a escribir")
        write_graph_with_node_names(physical_graph, "networks/" + physical_name)
    
    def save_logic(self, x_coordinates, y_coordinates, pg_exponent, n_dependence, version="", model=""):
        logic_graph = self.AS_network
        if not os.path.exists('networks'):
            os.makedirs('networks')
        # write logic
        logic_name = csv_title_generator("logic", x_coordinates, y_coordinates, pg_exponent, version=version, model=model)
        write_graph_with_node_names(logic_graph, "networks/" + logic_name)

    def save_to_pdf(self, x_coordinates, y_coordinates, pg_exponent, n_dependence, version="", model=""):           
        dependences_graph = self.interactions_network
        p_provider = list(self.physical_providers)
        l_providers = list(self.AS_providers)
        len_l_providers = len(l_providers)

        if not os.path.exists('networks'):
            os.makedirs('networks')
            
        # write dependence
        dependence_name = csv_title_generator("dependence", x_coordinates, y_coordinates, pg_exponent, n_dependence,
                                              len_l_providers, version=version, model=model)
        write_graph_with_node_names(dependences_graph, "networks/" + dependence_name)
        # write providers
        providers_name = csv_title_generator("providers", x_coordinates, y_coordinates, pg_exponent, n_dependence,
                                             len_l_providers, version=version, model=model)
        with open("networks/" + providers_name, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["logic"])
            for i in range(len(l_providers)):
                writer.writerow([l_providers[i]])
            writer.writerow(["physical"])
            for i in range(len(p_provider)):
                writer.writerow([p_provider[i]])

    def create_from_csv(self, AS_net_csv, physical_net_csv, interactions_csv, nodes_tittle, providers_csv="", AS_provider_nodes=[],
                        physical_provider_nodes=[]):
        # Create AS graph from csv file
        self.AS_network = set_graph_from_csv(AS_net_csv)
        # Create physical graph from csv file
        self.physical_network = set_graph_from_csv(physical_net_csv)
        x_coordinates, y_coordinates = get_list_of_coordinates_from_csv(nodes_tittle)
        self.physical_network.vs['x_coordinate'] = x_coordinates
        self.physical_network.vs['y_coordinate'] = y_coordinates

        # Create interactions graph from csv file. This contains the nodes of both networks
        self.interactions_network = igraph.Graph()
        self.interactions_network = set_graph_from_csv(interactions_csv)
        # set providers from file
        if providers_csv is not "":
            AS_provider_nodes = []
            physical_provider_nodes = []
            with open(providers_csv, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar=',')
                type_of_provider = ""
                for row in reader:
                    if row[0] == "logic":
                        type_of_provider = "logic"
                    elif row[0] == "physical":
                        type_of_provider = "physical"
                    else:
                        if type_of_provider == "logic":
                            AS_provider_nodes.append(str(row[0]))
                        if type_of_provider == "physical":
                            physical_provider_nodes.append(str(row[0]))

        as_net_name_list = self.AS_network.vs['name']
        physical_net_name_list = self.physical_network.vs['name']
        type_list = []
        for node in self.interactions_network.vs:
            if node['name'] in as_net_name_list:
                type_list.append(0)
            elif node['name'] in physical_net_name_list:
                type_list.append(1)
        self.interactions_network.vs['type'] = type_list
        # save provider nodes
        self.AS_providers = AS_provider_nodes
        self.physical_providers = physical_provider_nodes
        # save initial set of functional nodes
        self.initial_number_of_functional_nodes_in_AS_net = \
            len([a for a in self.AS_network.vs if self.AS_network.degree(a.index) > 0])
        return self

    def get_as(self):
        return self.AS_network

    def add_edges_to_physical_network(self, edge_tuple_array):
        (self.physical_network).add_edges(edge_tuple_array)

    def get_as_providers(self):
        return self.AS_providers

    def get_phys(self):
        return self.physical_network

    def get_phys_providers(self):
        return self.physical_providers

    def get_interd(self):
        return self.interactions_network
    
    def set_AS(self, AS_graph):
        # save AS graph (create copy from original)
        self.AS_network = igraph.Graph([e.tuple for e in AS_graph.es])
        self.AS_network.vs["name"] = AS_graph.vs["name"]
        return self
    
    def set_physical(self, physical_graph):
        self.physical_network = igraph.Graph([e.tuple for e in physical_graph.es])
        self.physical_network.vs["name"] = physical_graph.vs["name"]
        return self


    def create_from_graph(self, AS_graph, AS_provider_nodes, physical_graph, physical_provider_nodes,
                          interactions_graph):
        # save AS graph (create copy from original)
        self.AS_network = igraph.Graph([e.tuple for e in AS_graph.es])
        self.AS_network.vs["name"] = AS_graph.vs["name"]
        # save physical graph (create copy from original)
        self.physical_network = igraph.Graph([e.tuple for e in physical_graph.es])
        self.physical_network.vs["name"] = physical_graph.vs["name"]
        self.physical_network.vs["x_coordinate"] = physical_graph.vs["x_coordinate"]
        self.physical_network.vs["y_coordinate"] = physical_graph.vs["y_coordinate"]
        # prepare and save interactions graph
        self.interactions_network = igraph.Graph([e.tuple for e in interactions_graph.es])
        self.interactions_network.vs["name"] = interactions_graph.vs["name"]
        as_net_name_list = self.AS_network.vs["name"]
        physical_net_name_list = self.physical_network.vs["name"]
        type_list = []
        for node in self.interactions_network.vs:
            if node['name'] in as_net_name_list:
                type_list.append(0)
            elif node['name'] in physical_net_name_list:
                type_list.append(1)
        self.interactions_network.vs['type'] = type_list
        # save provider nodes
        self.AS_providers = AS_provider_nodes
        self.physical_providers = physical_provider_nodes
        # save initial set of functional nodes
        self.initial_number_of_functional_nodes_in_AS_net = \
            len([a for a in self.AS_network.vs if self.AS_network.degree(a.index) > 0])
        return self
    
    def create_from_empty_logic_physical(self, AS_graph_nodes_ids, AS_provider_nodes, physical_nodes_ids, physical_provider_nodes,
                          interactions_graph):
        """ # save AS graph (create copy from original)
        self.AS_network = igraph.Graph([e.tuple for e in AS_graph.es])
        self.AS_network.vs["name"] = AS_graph.vs["name"]
         # save physical graph (create copy from original)
        self.physical_network = igraph.Graph([e.tuple for e in physical_graph.es])
        self.physical_network.vs["name"] = physical_graph.vs["name"] """
        # prepare and save interactions graph
        self.interactions_network = igraph.Graph([e.tuple for e in interactions_graph.es])
        self.interactions_network.vs["name"] = interactions_graph.vs["name"]
        as_net_name_list = AS_graph_nodes_ids
        physical_net_name_list = physical_nodes_ids
        type_list = []
        for node in self.interactions_network.vs:
            if node['name'] in as_net_name_list:
                type_list.append(0)
            elif node['name'] in physical_net_name_list:
                type_list.append(1)
        self.interactions_network.vs['type'] = type_list
        # save provider nodes
        self.AS_providers = AS_provider_nodes
        self.physical_providers = physical_provider_nodes
        """ # save initial set of functional nodes
        self.initial_number_of_functional_nodes_in_AS_net = \
            len([a for a in self.AS_network.vs if self.AS_network.degree(a.index) > 0]) """
        return self

    def attack_nodes(self, list_of_nodes_to_delete):
        current_graph_A = self.AS_network
        current_graph_B = self.physical_network
        current_interaction_graph = self.interactions_network

        while True:
            # if there are no more nodes to delete, i.e, the network has stabilized, then stop
            if len(list_of_nodes_to_delete) == 0:
                break
            # Delete the nodes to delete on each network, including the interactions network
            nodes_to_delete_in_A = [node for node in list_of_nodes_to_delete if node in current_graph_A.vs['name']]
            nodes_to_delete_in_B = [node for node in list_of_nodes_to_delete if node in current_graph_B.vs['name']]
            current_graph_A.delete_vertices(nodes_to_delete_in_A)
            current_graph_B.delete_vertices(nodes_to_delete_in_B)
            current_interaction_graph.delete_vertices(
                [n for n in list_of_nodes_to_delete if n in current_interaction_graph.vs['name']])

            # Determine all nodes that fail because they don't have connection to a provider
            nodes_without_connection_to_provider_in_A = set(range(len(current_graph_A.vs)))
            alive_nodes_in_A = current_graph_A.vs['name']
            for provider_node in self.AS_providers:
                if provider_node not in alive_nodes_in_A:
                    continue
                length_to_provider_in_network_A = current_graph_A.shortest_paths(provider_node)[0]
                zipped_list_A = zip(length_to_provider_in_network_A, range(len(current_graph_A.vs)))
                current_nodes_without_connection_to_provider_in_A = \
                    set([a[1] for a in zipped_list_A if a[0] == float('inf')])
                nodes_without_connection_to_provider_in_A = \
                    nodes_without_connection_to_provider_in_A \
                        .intersection(current_nodes_without_connection_to_provider_in_A)

            nodes_without_connection_to_provider_in_B = set(range(len(current_graph_B.vs)))
            alive_nodes_in_B = current_graph_B.vs['name']
            for provider_node in self.physical_providers:
                if provider_node not in alive_nodes_in_B:
                    continue
                # print provider_node, "is alive"
                length_to_provider_in_network_B = current_graph_B.shortest_paths(provider_node)[0]
                zipped_list_B = zip(length_to_provider_in_network_B, range(len(current_graph_B.vs)))
                current_nodes_without_connection_to_provider_in_B = \
                    set([a[1] for a in zipped_list_B if a[0] == float('inf')])
                nodes_without_connection_to_provider_in_B = \
                    nodes_without_connection_to_provider_in_B \
                        .intersection(current_nodes_without_connection_to_provider_in_B)
            # save the names (unique identifier) of the nodes lost because can't access a provider
            names_of_nodes_lost_in_A = set(current_graph_A.vs(list(nodes_without_connection_to_provider_in_A))['name'])
            names_of_nodes_lost_in_B = set(current_graph_B.vs(list(nodes_without_connection_to_provider_in_B))['name'])
            # Delete all nodes that fail because they don't have connection to a provider on each network including
            # interactions network
            current_graph_A.delete_vertices(nodes_without_connection_to_provider_in_A)
            current_graph_B.delete_vertices(nodes_without_connection_to_provider_in_B)
            nodes_to_delete = list(names_of_nodes_lost_in_A.union(names_of_nodes_lost_in_B))
            current_interaction_graph.delete_vertices(
                [n for n in nodes_to_delete if n in current_interaction_graph.vs['name']])
            # Get the nodes lost because they have lost all support from the other network
            zipped_list_interactions = zip(current_interaction_graph.degree(), current_interaction_graph.vs['name'])
            # Add them to the nodes to delete on the next iteration
            list_of_nodes_to_delete = [a[1] for a in zipped_list_interactions if a[0] < 1]

        return self

    def get_ratio_of_funtional_nodes_in_AS_network(self):
        functional_nodes_in_AS_net = len([a for a in self.AS_network.vs if self.AS_network.degree(a.index) > 0])
        return (functional_nodes_in_AS_net * 1.0) / (self.initial_number_of_functional_nodes_in_AS_net * 1.0)

    def node_mtfr(self):
        return len((self.interactions_network.maximum_bipartite_matching()).edges())

