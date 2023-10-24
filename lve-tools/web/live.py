import subprocess

def ensure_npx_available():
    try:
        subprocess.check_call(['npx', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        raise RuntimeError("'npx' is not installed. Please install it with `npm install -g npx`")

def ensure_onchange_available():
    try:
        subprocess.check_call(['npx', 'onchange', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        raise RuntimeError("'onchange' is not installed. Please install it with `npm install -g onchange`")

def ensure_live_server_available():
    try:
        subprocess.check_call(['npx', 'live-server', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        raise RuntimeError("'live-server' is not installed. Please install it with `npm install -g live-server`")
    
if __name__ == '__main__':
    ensure_npx_available()
    ensure_onchange_available()
    ensure_live_server_available()

    print("> onchange ../lve_tools/**/* ../../repository/**/* ./*.html ../../docs/**/* ./static/**/* ./*.py generator/**/*.py -- python make.py")
    # with shell
    watcher = subprocess.Popen('onchange ../lve_tools/**/* ../../repository/**/* ./*.html ../../docs/**/* ./static/**/* ./*.py generator/**/*.py -- python make.py', shell=True)
    server = subprocess.Popen(['npx', 'live-server'], cwd='build')

    try:
        watcher.wait()
    except KeyboardInterrupt:
        server.kill()
        watcher.kill()
        print("Killed watcher and server")