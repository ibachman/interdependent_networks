import http.client
import json


def get_lines_from_json(json_data):
    data = json.load(json_data)
    lines = []
    for index in data:
        lines.append({"job_id": data[index]["id"],
                      "line": data[index]["instruction"]})
    return lines


class ConnectionManager:
    server_name = ""
    connection = None
    machine_name = None

    def __init__(self, server_name):
        self.server_name = server_name
        self.connection = http.client.HTTPConnection(server_name)

    def set_machine_name(self, machine_name):
        self.machine_name = machine_name

    def set_job_done(self, job_id):
        uri = "/job_done/" + str(job_id)
        self.connection.request("GET", uri)

    def get_jobs_from_server(self, n_workers):
        uri = "/get_jobs/" + str(n_workers)
        if self.machine_name:
            uri += "?machine="+str(self.machine_name)
        print(uri)
        self.connection.request("GET", uri)
        json_data = self.connection.getresponse()
        return get_lines_from_json(json_data)
