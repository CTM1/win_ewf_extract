class ArtifactExtractor:
    def process_fs_object(self, fs_object):
        raise NotImplementedError("Subclasses must implement this method.")
    # TODO: set starting_path, processable_file_names and processable_directories as mandatory attributes.