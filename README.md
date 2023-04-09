This project extracts and parses interesting files and data from a Windows EWF
image.

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
# Usage

You can use the `-h` flag to get help, here is an example of how you'd use this tool:

```
$ python3 win_ewf_extractor.py -c config/events.yml -o output -f images/Disk_Image.E01
```

This would extract Event Logs from the journals defined in the `config/events.yml` configuration. More configurations are available in `config` to match your needs.

# Documentation
Documentation is made using [sphynx](), once the [requirements](#Requirements) are installed, you can generate it with

```
cd docs/ && make html && python3 -m http.server
```

Documentation will be disponible in your favorite web browser at [https://localhost:8000/](https://127.0.0.1:8000)

Alternatively, you can read the PDF file named doc.pdf.

# Current Work

- [x] Extract MFT
    - [x] Parse MFT and extract information to .csv
    - [ ] Leverage the analyzeMFT options to allow more precise information through configs
- [x] Extract Event Logs
    - [x] Parse Event Logs and extract them to an .xml file, filter them by EventIDs.
- [x] Extract Registry Hives
    - [x] Parse Registry and Backup registry hives for keys, values, and creation date
    - [ ] Implement deeper information by correlating with transaction logs - https://www.mandiant.com/resources/blog/digging-up-the-past-windows-registry-forensics-revisited
    - [ ] Get previously deleted keys and values
- [ ] Extract Browser Artifacts
    - [x] Google Chrome
        - [x] Extract relevant SQLite3 files
        - [ ] Parse information to human readable format
        - [ ] See if we can decrypt information if DPAPI keys are present on disk - https://www.coresecurity.com/core-labs/articles/reading-dpapi-encrypted-keys-mimikatz
            - [ ] Works with unprotected keys
            - [ ] Unprotect keys using a given password or by brute-forcing methods
    - [x] Microsoft Edge
        - [x] Extract relevant SQLite3 files
        - [ ] Parse information to human readable format
        - [ ] See if we can decrypt information if DPAPI keys are present on disk
            - [ ] Works with unprotected keys
            - [ ] Unprotect keys using a given password or by brute-forcing methods
    - [ ] Firefox
        - [ ] Extract relevant SQLite3 files
        - [ ] Parse information to human readable format
        - [ ] See if we can decrypt information if DPAPI keys are present on disk
            - [ ] Works with unprotected keys
            - [ ] Unprotect keys using a given password or by brute-forcing methods
            

