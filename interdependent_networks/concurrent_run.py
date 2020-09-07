from interdependent_networks.runnables import run_test, add_edges
import multiprocessing
import argparse
import queue
import interdependent_networks.connection_manager as cm


def worker_run(worker_queue):
    print('worker running')
    while True:
        try:
            task = worker_queue.get(timeout=60)
        except queue.Empty:
            break
        print('borking - ' + str(multiprocessing.current_process().name))
        process_name = str(multiprocessing.current_process().name)
        if task['make_edges']:
            add_edges(task['x_coordinate'], task['y_coordinate'], task['exp'], task['n_inter'],
                      task['n_logic_suppliers'], task['version'], task['n_logic'], task['n_phys'],
                      task['iter'], task['model'], task['phys_iteration'], task['strategy'])
        else:
            run_test(task['x_coordinate'], task['y_coordinate'], task['exp'], task['n_inter'],
                     task['n_logic_suppliers'], task['version'], task['n_logic'], task['n_phys'],
                     task['iter'], task['READ_flag'], task['attack_type'], task['model'], task['logic'],
                     task['physical'], task['phys_iteration'], task['strategy'], process_name=process_name)
        # avisar que job_done (task["job_id"])
        if task["job_id"] > -1:
            task["server_connection"].set_job_done(task["job_id"])
            print("[COMPLETED] Job {} completed".format(task["job_id"]))
        worker_queue.task_done()
        if worker_queue.empty():
            break
    print('[FINISHED] Finished batch')


def run_from_static_params(max_workers):
    print('Running from static parameters')
    work_queue = multiprocessing.JoinableQueue()
    the_pool = multiprocessing.Pool(max_workers,
                                    worker_run,
                                    (work_queue,))  # <-- The trailing comma is necessary!
    the_pool.close()

    n_logic = 10
    n_phys = 20
    n_inter = 3
    n_logic_suppliers = 3
    x_dim = 400
    y_dim = 400
    exp = 2.5
    at_type = 'physical'
    for i in range(5):
        new_task = {}
        new_task['x_coordinate'] = x_dim
        new_task['y_coordinate'] = y_dim
        new_task['exp'] = exp
        new_task['n_inter'] = n_inter
        new_task['n_logic_suppliers'] = n_logic_suppliers
        new_task['version'] = i
        new_task['n_logic'] = n_logic
        new_task['n_phys'] = n_phys
        new_task['attack_type'] = at_type
        new_task['READ_flag'] = False
        work_queue.put(new_task)
    work_queue.close()
    work_queue.join()


def parse_task_args(line):
    task = {}
    args = parser.parse_args(line.split())
    task['x_coordinate'] = args.xcoordinate
    task['y_coordinate'] = args.ycoordinate
    task['exp'] = args.exponentpg
    task['n_inter'] = args.interdependenceamount
    task['n_logic_suppliers'] = args.logicsuppliers
    task['version'] = args.version
    task['n_logic'] = args.logicnodes
    task['n_phys'] = args.physicalnodes
    task['iter'] = args.iterations
    task['attack_type'] = args.attack_types
    task['READ_flag'] = args.read
    task['model'] = args.model
    task['logic'] = args.logic
    task['physical'] = args.physical
    task['phys_iteration'] = args.physiteration
    task['strategy'] = args.strategy
    task['make_edges'] = args.makeedges

    return task


def run_from_file(max_workers, filename, file_lines=[]):
    file_lines = [int(l) for l in file_lines]
    with open(filename) as f:
        lines = [line.rstrip('\n') for line in f.readlines()]
        lines = [lines[i] for i in file_lines]
    run_command_lines(max_workers, lines)


def run_command_lines(max_workers, command_lines, from_server=False):
    job_id = -1
    work_queue = multiprocessing.JoinableQueue()
    the_pool = multiprocessing.Pool(max_workers,
                                    worker_run,
                                    (work_queue,))  # <-- The trailing comma is necessary!
    the_pool.close()
    for job in command_lines:
        if from_server:
            line = job["line"]
            job_id = job["job_id"]
        new_task = parse_task_args(line)
        new_task["job_id"] = job_id
        new_task["server_connection"] = from_server
        work_queue.put(new_task)
    work_queue.close()
    work_queue.join()


parser = argparse.ArgumentParser(description="Run experiments with the given variables")
parser.add_argument('-ln', '--logicnodes', type=int, help='amount of nodes in the logic network')
parser.add_argument('-pn', '--physicalnodes', type=int, help='amount of nodes in the physical network')
parser.add_argument('-ia', '--interdependenceamount', type=int, help='maximum amount of interconnections')
parser.add_argument('-ls', '--logicsuppliers', type=int, help='amount of suppliers in the logic network')
parser.add_argument('-e', '--exponentpg', type=float, help='lambda exponent for logic network Power-Law')
parser.add_argument('-x', '--xcoordinate', type=int, help='width of the physical space for the physical network')
parser.add_argument('-y', '--ycoordinate', type=int, help='length of the physical space for the physical network')
parser.add_argument('-v', '--version', type=int, help='version for this kind of interdependent systems')
parser.add_argument('-i', '--iterations', type=int, help='Number of iterations to perform')
parser.add_argument('-r', '--read', action='store_true', help='If this is specified will read the networks from file')
parser.add_argument('-at', '--attack_types', type=str, nargs='?', const='', default='physical,logic,both',
                    help='Optional argument. Type of attack to simulate, valid values are physical, logic and both')
parser.add_argument('-m', '--model', type=str, nargs='?', const='', default='MRN,GG,5NN',
                    help='Optional argument. Type of Physical Network to simulate, valid values are MRN, GG and 5NN')
parser.add_argument('-l', '--logic', action='store_true', help='If this is specified will create logic layer')
parser.add_argument('-p', '--physical', action='store_true', help='If this is specified will create physical network')
parser.add_argument('-it', '--physiteration', type=int, help='Number of iteration when creating set of edges', default=0)
parser.add_argument('-st', '--strategy', type=str, help='Strategy for adding new edges', default='')
parser.add_argument('-me', '--makeedges', action='store_true', help='Create extra edges for strategy')


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Run experiments concurrently")
    argument_parser.add_argument('-w', '--workers', type=int,
                                 help='amount of concurrent workers, if empty will default to number of cpus')
    argument_parser.add_argument('-f', '--from_file', type=str,
                                 help='filename containing the tasks parameters, if empty will use static parameters')
    argument_parser.add_argument('-l', '--line', type=str,
                                 help='line containing the instruction to run', default=-1)
    argument_parser.add_argument('-g', '--getlinesfrom', type=str,
                                 help='receives url to retreive lines', default=-1)


    args = argument_parser.parse_args()
    n_workers = args.workers
    arg_file = args.from_file
    file_line = args.line
    get_lines_from = args.getlinesfrom
    if file_line > 0:
        file_lines = ((file_line.replace("(", "")).replace(")", "")).split(",")
    if n_workers is None:
        n_workers = multiprocessing.cpu_count()
    if arg_file is not None:
        run_from_file(n_workers, arg_file)
    if get_lines_from is not None:
        server_connection = cm.ConnectionManager(get_lines_from)
        lines = server_connection.get_jobs_from_server(n_workers)
        print(lines)
        n_lines = len(lines)
        if n_lines > 0:
            if n_lines < n_workers:
                rest = n_workers - n_lines
                print("[FREE CORES] received {} jobs for {} cores, {} cores available".format(n_lines, n_workers, rest))
                n_workers = len(lines)
            run_command_lines(n_workers, lines, from_server=server_connection)
        else:
            print("[EMPTY ANSWER] No lines received")

# TODO : manejar el caso cuando legue lista vacía de jobs y hacer job_done al final