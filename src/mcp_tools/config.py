import os
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()

def load_environment_vars(conf: dict) -> dict:
    for tool, config in conf['mcpServers'].items():
        for property in config.keys():
            if property == 'env':
                for k, v in config[property].items():
                    if isinstance(v, str) and v.startswith("${"):
                        env_var_name = v[2:-1]
                        env_var_val = os.environ.get(env_var_name, None)
                        if env_var_val is None:
                            raise ValueError(f"Environment variable {env_var_val} is not set")
                        conf["mcpServers"][tool][property][k] =  env_var_val
            if property == 'args':
                for i,arg in enumerate(config[property]):
                    if isinstance(arg, str) and arg.startswith("${"):
                        env_var_name = arg[2: -1]
                        env_var_val = os.environ.get(env_var_name, None)
                        if env_var_val is None:
                            raise ValueError(f"Environment variable {env_var_val} is not set")
                        conf["mcpServers"][tool][property][i] =  env_var_val
    return conf["mcpServers"]


conf_file = Path(__file__).parent / "mcp_config.json"
if not conf_file:
    raise FileNotFoundError(f"mcp.config.json file {conf_file} does not exist")

with open(conf_file, 'r') as f:
    config = json.load(f)

mcp_config = load_environment_vars(config)

