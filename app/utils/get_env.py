from os import environ

def get_env_val_or_raise(env_name: str) ->str:
    try:
        return environ[env_name]
    except KeyError:
        raise RuntimeError(f"Required environment variable {env_name} is not set")
    
def get_env_val(env_name: str, default=None) -> str|None:
    return environ.get(env_name, default)