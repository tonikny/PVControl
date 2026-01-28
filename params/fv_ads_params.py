import importlib.util

def load_parametros(path):
    spec = importlib.util.spec_from_file_location("Parametros_FV", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

