This project extracts and parses interesting files and data from a Windows EWF
image.

The main extracted files are:
    - System registry
    - User hives
    - Internet Navigator History:
        - Edge
        - Internet Explorer
        - Firefox
        - Chrome
    - The MFT
    - Windows Event Logs

# Documentation
Documentation is made using [sphynx](), once the [requirements](#Requirements) are installed, you can generate it with

```
cd docs/ && make html && python3 -m http.server
```

Documentation will be disponible in your favorite web browser at [https://localhost:8000/](https://127.0.0.1:8000)

Alternatively, you can read the PDF file named doc.pdf.

# Requirements
Python dependencies can be installed with using pip::

```
$ python3 -m pip install -r requirements.txt
```

You will also need `sleuthkit` and `libtsk19` installed:

[Installation manual here](https://github.com/sleuthkit/sleuthkit/blob/develop/INSTALL.txt)

On debian based systems::

```
# apt-get install sleuthkit libtsk19
```
