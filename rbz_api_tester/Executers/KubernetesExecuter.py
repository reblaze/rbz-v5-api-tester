import subprocess
import re

from typing import List
from kubernetes import client, config

from rbz_api_tester.Param import Param
from rbz_api_tester.utils import get_my_external_ip
from rbz_api_tester.CommonParameters import CommonParameters


class KubernetesExecuter:
    cluster: str
    container: str
    pod: str
    pods: List[str]
    params: List[Param]

    def __init__(
        self,
        params: List[Param],
    ):
        self.pods = list()
        self.params = params
        self.container = self._get("container")
        self.pod = self._get("pod")
        self.cluster = self._get_cluster()
        self._use_kube_context()
        self._get_pods()

    def _get_cluster(self) -> str:
        cluster = self._get("cluster")
        if cluster == "brokers":
            return CommonParameters.broker_cluster_name
        elif cluster == "control":
            return CommonParameters.control_cluster_name
        elif cluster == "data":
            return CommonParameters.data_cluster_name
        else:
            raise Exception(
                f"Invalid culster type: {cluster}, please pass only brokers, control or data"
            )

    def _get(self, name: str) -> str:
        for param in self.params:
            if param.key == name:
                value = param.value
                value = value.replace("@@branch@@", CommonParameters.branch)
                value = value.replace("@@ip@@", get_my_external_ip())
                return value
        raise Exception("Could not find {name} argument")

    def _use_kube_context(self):
        config.load_kube_config()
        config.kube_config.load_kube_config(context=self.cluster)

    def _get_pods(self):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pods_list = v1.list_namespaced_pod(CommonParameters.planet)
        pattern = re.compile(self.pod)

        for pod in pods_list.items:
            match = re.match(pattern, pod.metadata.name)
            if match:
                CommonParameters.logger.info(f"Pod Name: {pod.metadata.name}")
                CommonParameters.logger.info(f"Pod Status: {pod.status.phase}")
                self.pods.append(pod.metadata.name)

    def _core_execute(self, command_str: str, pod: str) -> (str, str):
        command = ["/bin/sh", "-c", command_str]
        kubectl_command = [
            "kubectl",
            "exec",
            "-it",
            f"--namespace={CommonParameters.planet}" if CommonParameters.planet else "",
            f"--container={self.container}" if self.container else "",
            pod,
            "--",
        ] + command

        process = subprocess.Popen(
            kubectl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = process.communicate()
        CommonParameters.logger.info(f"command executes on pod: {pod}")
        if len(output) > 0:
            CommonParameters.logger.info(output.decode("utf-8"))
        if len(error) > 0:
            CommonParameters.logger.error(error.decode("utf-8"))
        return (output, error)

    def _execute_command_on_pod(self, command: str, all: bool) -> (str, str):
        out = ""
        err = ""
        if not all and len(self.pods) > 0:
            (out, err) = self._core_execute(command, self.pods[0])
        else:
            for pod in self.pods:
                (out_p, err_p) = self._core_execute(command, pod)
                if len(out):
                    out = f"{out}\n{out_p}"
                else:
                    out = out_p

                if len(err):
                    err = f"{err}\n{err_p}"
                else:
                    err = err_p

        return (out, err)

    def _core_copy(
        self, source_path: str, destination_path: str, pod: str
    ) -> (str, str):
        kubectl_command = [
            "kubectl",
            "cp",
            f"{CommonParameters.planet}/{pod}:{source_path}",
            destination_path,
        ]

        if self.container:
            kubectl_command.insert(2, f"--container={self.container}")

        process = subprocess.Popen(
            kubectl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = process.communicate()

        if len(output) > 0:
            CommonParameters.logger.info(output.decode("utf-8"))
        if len(error) > 0:
            CommonParameters.logger.error(error.decode("utf-8"))

        return (output, error)

    def _copy_file_from_pod(
        self, source_path: str, destination_path: str, all: bool
    ) -> (str, str):
        out = ""
        err = ""
        if not all and len(self.pods) > 0:
            (out, err) = self._core_copy(source_path, destination_path, self.pods[0])
        else:
            for pod in self.pods:
                (out_p, err_p) = self._core_copy(source_path, destination_path, pod)
                if len(out):
                    out = f"{out}\n{out_p}"
                else:
                    out = out_p

                if len(err):
                    err = f"{err}\n{err_p}"
                else:
                    err = err_p

        return (out, err)

    def execute(self) -> (str, str):
        operation = self._get("operation")
        if operation == "copy":
            res = self._copy_file_from_pod(
                self._get("source"), self._get("destination"), False
            )
        elif operation == "run":
            res = self._execute_command_on_pod(self._get("command"), False)
        else:
            raise Exception(
                f"Unsupported operation: {operation}, supported operations are execute or copy"
            )

        return res
