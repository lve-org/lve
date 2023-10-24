# LVE Web Interface

To build a local version of the LVE web interface, run the following commands:

```
# install lve-tools with the additional requirements for the web interface
pip install 'lve-tools[web]'
```

To continously build and serve the web interface (hot-reloading), run the following command:

```
python live.py
```

For this, the [Node.js](https://nodejs.org/en/)-based tools `onchange` and `live-server` are required.

## Web Interface Development

The web interface is a static site generated from the `../../repository` directory. The main entry point for 
building the site is the `make.py` file. 