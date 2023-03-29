# Requirements

You should have `sleuthkit` and `libtsk19` installed.

On Debian-based systems:

`sudo apt-get install sleuthkit libtsk19`

If you don't have the sleuthkit package, you can read here about how to install it:

https://github.com/sleuthkit/sleuthkit/blob/develop/INSTALL.txt

# Project Goals
This project aims to write a python script using sleuthkit as a backend that will extract at least the following files:

- [x] Windows System registries
- [ ] Windows User Hives
- [ ] Internet Edge user files
- [ ] Internet Explorer user files
- [ ] Firefox user files
- [ ] Chrome user files
- [ ] Windows evtx files, at least security and system
- [ ] the MFT
