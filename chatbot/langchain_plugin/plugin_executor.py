from typing import Iterable
from dataclasses import dataclass
from .command_executor import CommandExecutor
import time
import re
import copy

def replace_multiple_whitespaces_and_commas_with_comma(input_string: str) -> str:
    output_string = re.sub(r'[\s,]+', ',', input_string)
    return output_string

@dataclass
class Plugin:
    value: str
    path: str

PLUGIN_FOLDER_BASE = "langchain_plugin/agents"
GOOGLE_SEARCH = "google_search"
all_plugins = {
    value : Plugin(value, path) for value, path in [
        (GOOGLE_SEARCH, f"{PLUGIN_FOLDER_BASE}/google_search_agent.py")
    ]
}


def get_all_plugin_values() -> list[str]:
    return list(all_plugins.keys())

def get_plugin(plugin_name: str) -> Plugin:
    if plugin_name not in all_plugins.keys():
        raise ValueError(f"plugin_name: {plugin_name} is not supported, please choose from {all_plugins.keys()}")

    return all_plugins[plugin_name]

class PluginExecutor:
    def __init__(self, plugin: Plugin) -> None:
        self.plugin = plugin
        self.final_logs = []

    def execute(self, prompt: str, plugin_param: dict[str, str]) -> Iterable[list[str]]:

        param_string = " ".join([f"{key}{value}" for key, value in plugin_param.items()])

        cmd = f"python3 -u {self.plugin.path} {param_string} -p '{replace_multiple_whitespaces_and_commas_with_comma(prompt)}'"
        
        cmd_executor = CommandExecutor()
        cmd_executor.execute(cmd)
        while cmd_executor.is_executing:
            log = cmd_executor.get_log()
            if len(log) == 0:
                time.sleep(0.1)
                continue
            yield log
            time.sleep(0.1)
        self.final_logs = copy.deepcopy(cmd_executor.logs_queue)
    
    def get_logs(self) -> str:
        return "\n".join(self.final_logs)


