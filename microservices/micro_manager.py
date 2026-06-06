from pathlib import Path
import subprocess
import sys


class MicroserviceManager:
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.processes = {}

    def start_all(self):
        if not self.directory.exists():
            raise FileNotFoundError(
                f"Microservice directory not found: {self.directory}"
            )
        for script in self.directory.glob("*.py"):
            self.start_service(script)

    def stop_all(self):
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)

    def start_service(self, script_path):
        script_path = Path(script_path)
        if script_path.name in self.processes:
            return
        print(f"Starting microservice: {script_path.name}")
        process = subprocess.Popen(
            [sys.executable, str(script_path.resolve())],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        self.processes[script_path.name] = process

    def stop_service(self, service_name: str):
        process = self.processes.get(service_name)
        if process is None:
            return
        print(f"Stopping microservice: {service_name}")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        del self.processes[service_name]
