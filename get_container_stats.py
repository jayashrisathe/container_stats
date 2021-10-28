
import docker
import requests
import json
client = docker.from_env()
client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
def convert_in_unicode(str):
    return unicode(str, "utf-8")

def calculate_cpu_percent(d):
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                   float(d["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent

#df_dict = client.df()
#print("df--------------------------------", df_dict)

def get_curent_stats():
    """ Returns list of dictionary containing current stats of containers """
    print("I am here===============")
    counter = 0
    list_to_return = []
    for container in client.containers.list():
        print("I==", container.name, container.id)

        complete_dict = container.stats(stream=False)
#        cpu_details_key = unicode("cpu_stats", "utf-8")
#        memory_details_key = unicode("memory_stats", "utf-8")
        cpu_per = calculate_cpu_percent(complete_dict)
        # print("percent===========", cpu_per)
        container_stats = {
                          'cpu_usage': cpu_per,
#                          'memory_limit': complete_dict.get(memory_details_key).get(convert_in_unicode('limit')),
#                          'memory_usage': complete_dict.get(memory_details_key).get(convert_in_unicode('usage')),
                          'container_name': container.name,
                          'container_image': container.id,
                          }

        print("\n\ndata_to_return -------", container_stats)
        list_to_return.append(container_stats)
        
        counter = counter + 1
        if counter == 6:
            break
    return list_to_return

#get_curent_stats()
if __name__ == '__main__':
    data = get_curent_stats()
    print("Data==============", data[0], type(data[0]))
    res = requests.post('http://localhost:8080/stats', json.dumps(data[0]))
    print("res----------------", res)
