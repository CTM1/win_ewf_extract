Welcome to Windows EWF Extractor's documentation!
=================================================

.. automodule:: win_ewf_extractor

Usage
=====
.. argparse::
   :module: win_ewf_extractor
   :func: make_parser
   :prog: win_ewf_extractor.py

Requirements
============
Python dependencies can be installed with using pip::

$ python3 -m pip install -r requirements.txt

You will also need `sleuthkit` and `libtsk19` installed:

`Installation manual here <https://github.com/sleuthkit/sleuthkit/blob/develop/INSTALL.txt>`_

On debian based systems::

# apt-get install sleuthkit libtsk19

Internals
=========

.. autoclass:: modules.artifact_extraction.ArtifactExtractor
.. autoclass:: modules.disk_utils.EWFImgInfo
.. autofunction:: modules.disk_utils.find_file_systems
.. autofunction:: modules.disk_utils.find_file

.. autoclass:: modules.registry.RegistryExtractor

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
