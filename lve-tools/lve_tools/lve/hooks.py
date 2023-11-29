"""
Hooks represent a way to extend the functionality of the LVE Tools,
e.g. to monitor the number of LLM and checker calls.
"""

hooks = {}

def hook(tag, *args, **kwargs):
    for func in hooks.get(tag, []):
        func(*args, **kwargs)

def register_hook(tag, func):
    hooks.setdefault(tag, []).append(func)

def unregister_hook(tag, func):
    if tag in hooks:
        hooks[tag].remove(func)