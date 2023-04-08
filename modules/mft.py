import os
import subprocess
from modules.artifact_extraction import ArtifactExtractor
from analyzemft import mftsession


class MftExtractor(ArtifactExtractor):
    def __init__(self, output_dir, config):
        self.n_mft = 0
        # Path to output directory
        self.output_dir = output_dir
        # Output directory inside registry directory
        self.mft_output_dir = os.path.join(output_dir, "mft")

        try:
            os.mkdir(self.mft_output_dir)
        except FileExistsError:
            pass

        # File names to process if found on recurse_files, leave empty for all of them.
        # Do not use extensions for them !
        # TODO: Support extensions, as you can see, NTUSER.DAT is the prime example of why extensions
        # may not be as trivial as they should.

        self.processable_file_names = ["$mft"]

        # Certain process_fs_object calls may want to process entire directories.
        # Leave empty if it's files you want
        # Unimplemented for now TODO in disk_utils.py
        self.processable_directories = []

        # Starting path for files we're interested it, allows us to optimize recursion
        # by only recursing into directories we're interested in. Leave empty for all of them.
        # TODO: Should be a list of paths like filenames, implement in disk_utils.py
        self.starting_path = "\\".lower()

    def process_fs_object(self, fs_object, file_path):
        print("[+] Found an MFT file")
        print("[+] Writing MFT to disk")
        self.mft_file_writer(fs_object, "MFT", "({})".format(self.n_mft), self.mft_output_dir)

        print("[+] Parsing MFT to .csv")
        print("[*] This may take a while...")
        session = mftsession.MftSession()
        session.mft_options()
        session.options.filename = os.path.join(self.mft_output_dir, "MFT({})".format(self.n_mft))
        session.options.output = os.path.join(self.mft_output_dir, "MFT_output({}).csv".format(self.n_mft))

        try:
            with open(session.options.filename, 'x') as f:
                pass
        except FileExistsError:
            pass
        try:
            with open(session.options.output, 'x') as f:
                pass
        except FileExistsError:
            pass

        session.open_files()
        session.process_mft_file()
        self.n_mft += 1

    def mft_file_writer(self, fs_object, name, ext, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = name + ext
        outfile_path = os.path.join(output_dir, filename)

        with open(outfile_path, "wb") as outfile:
            outfile.write(fs_object.read_random(0, fs_object.info.meta.size))
