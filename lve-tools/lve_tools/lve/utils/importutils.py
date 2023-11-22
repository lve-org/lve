def installed(module_name):
    import importlib.util
    spec = importlib.util.find_spec(module_name)
    return spec

def ensure_installed(module_name, package=None, version=None, component=None):
    """
    Checks whether 'module_name' is installed. If not, raises a 
    RuntimeError with a helpful error message that tells the user 
    to install the package to use 'component' (if component is provided)
    """
    if not installed(module_name):
        msg = f"Failed to import module '{module_name}'. Please make sure the package {package or module_name} is installed, e.g. by running 'pip install {package or module_name}'."
        version = version if version is not None else ""
        if component is not None:
            msg = f"Failed to import module '{module_name}' required for the use of '{component}'. Please make sure the package '{package or module_name}{version}' is installed, e.g. by running 'pip install \"{package or module_name}{version}\"'."
        raise RuntimeError(msg)