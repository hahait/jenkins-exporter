from jenkins import Jenkins
import xmltodict
import requests
import time
from prometheus_client.core import GaugeMetricFamily


class JenkinsCollector(object):

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.jenkins = Jenkins(url=self.url, username=self.username, password=self.password) 

    def collect(self):
        jenkins_metrics = JenkinsMetrics(self.jenkins, self.url)
        metrics = jenkins_metrics.make_metrics()

        for metric in metrics:
            yield metric


class JenkinsMetrics(object):

    def __init__(self, jenkins, jenkins_url):
        self.jenkins = jenkins
        self.jenkins_url = jenkins_url
        self.metrics = []

    def get_user(self, build_info):

        b_actions = build_info.get("actions")

        user1 = user2 = None
        for i in b_actions:
            if i.get('_class') == 'hudson.model.ParametersAction':
                for j in i["parameters"]:
                    if j.get("name") == 'commit_user':
                        user1 = j.get("value") if j.get("value") else None
                        break
            if i.get('_class') == 'hudson.model.CauseAction':
                for j in i["causes"]:
                    if j.get("_class") == 'hudson.model.Cause$UserIdCause':
                        user2 = j.get("userId") if j.get("userId") else None
                        break

        if user1 and user1 != "hello":
            user = user1
        elif user2:
            user = user2
        else:
            user = "None"

        return user
    

    def make_metrics(self):
        metrics = []
        
        ''' 获取正在构建的 jobs '''
        metric = None
        metric = GaugeMetricFamily(
            'jenkins_job_building',
            'find the building jobs, and print the job start time',
            labels = ['job_name', 'user', 'number', 'node', 'url']
        )

        building_jobs_list = self.jenkins.get_running_builds()
        if not building_jobs_list :
            metric.add_metric(
                labels = [],
                value = 0
            )

        for job in building_jobs_list:

            job_name = job["name"]
            number = str(job["number"])
            node = job["node"]
            url = job["url"]
            
            try:
                job_info = self.jenkins.get_build_info(job_name,eval(number))
                start_time = job_info["timestamp"]
                user = self.get_user(job_info)
                metric.add_metric(
                    labels = [job_name, user, number, node, url],
                    value = start_time
                )
            except Exception as e:
                print("报错啦: ", e)

        metrics.append(metric)

        ''' 获取每个 job 每次 build 的耗时 '''
        metric_1 = GaugeMetricFamily(
            'jenkins_job_build_duration',
            'print per job and per build duration time',
            labels = ['job_name', 'user', 'number', 'node', 'url', 'result', 'start_time', 'building']
        )
    
        ''' 获取每个 build 的构建状态 '''
        metric_2 = GaugeMetricFamily(
            'jenkins_job_build_result',
            'print per job and per build result; 0-SUCCESS, 1-FAILURE, 2-ABORTED, 3-Others',
            labels = ['job_name', 'user', 'number', 'node', 'url', 'duration', 'start_time', 'building', 'in_3hours']
        )
        
        url = self.jenkins_url + "/rssLatest"
        r = requests.get(url)
        xml_data = xmltodict.parse(r.text)

        t = time.time()
        t_now = int(round(t * 1000))    
    
        for i in xml_data["feed"]["entry"]:
            try:
                aa = i["title"].split(' ')
                job_name = aa[0]
                number = aa[1].strip("#")
                b_info = self.jenkins.get_build_info(job_name, eval(number))
                duration = b_info["duration"]
                result = b_info["result"] if b_info["result"] else "Building"
                if result == 'SUCCESS':
                    status = 0
                elif result == 'FAILURE':
                    status = 1
                elif result == 'ABORTED':
                    status = 2
                else:
                    status = 3
                start_time = b_info["timestamp"]
                if t_now - start_time <= 10800000:
                    in_3hours = True
                else:
                    in_3hours = False
     
                node = b_info["builtOn"]
                url = b_info["url"]
                building = str(b_info["building"])
                user = self.get_user(b_info)
                metric_1.add_metric(
                    labels = [job_name, user, number, node, url, result, str(start_time), building],
                    value = duration
                )
                metric_2.add_metric(
                    labels = [job_name, user, number, node, url, str(duration), str(start_time), building, str(in_3hours)],
                    value = status
                )
            except Exception as e:
                print("报错啦: ", e)

        metrics.append(metric_1)
        metrics.append(metric_2)

        self.metrics = metrics
        return self.metrics
