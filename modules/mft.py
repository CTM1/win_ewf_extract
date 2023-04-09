import os
import subprocess
from modules.artifact_extraction import ArtifactExtractor
from analyzemft import mftsession


class MftExtractor(ArtifactExtractor):
    """MftExtractor is an implementation of ArtifactExtractor dedicated to
    extracting the MFT."""
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

        self.processable_file_names = ["$mft"]
        self.processable_directories = []
        self.starting_path = "\\".lower()

    def process_fs_object(self, fs_object, file_path):
        """Processes the MFT object using by extracting it to disk then using the analyzeMFT util.

        Args:
            fs_object (File): The MFT file
            file_path (Path): The MFT file path
        """
        print("[MftExtractor] [+] Found an MFT file")
        print("[MftExtractor] [+] Writing MFT to disk")
        self.mft_file_writer(fs_object, "MFT", "({})".format(self.n_mft), self.mft_output_dir)

        print("[MftExtractor] [+] Parsing MFT to .csv")
        print("[MftExtractor] [*] This may take a while...")
        session = mftsession.MftSession()
        session.mft_options()

        # Leave this, or conflicting argument parsing options will write into your .csv
        session.options.csvtimefile = None

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
            print("[MftExtractor] [+] Successful\n")
