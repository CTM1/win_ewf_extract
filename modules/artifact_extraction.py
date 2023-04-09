class ArtifactExtractor:
    """This class is an abstract class implemented by modules extracting and
    parsing a specific artifact."""

    def __init__(self):
        self._processable_file_names = []
        self._processable_directories = []
        self._starting_path = ""

    def process_fs_object(self, fs_object):
        raise NotImplementedError("Subclasses must implement this method.")

    @property
    def starting_path(self):
        if not self._starting_path:
            raise NotImplementedError("Subclasses must implement starting_path")
        return self._starting_path

    @starting_path.setter
    def starting_path(self, starting_path):
        self._starting_path = starting_path.lower()             # TODO: must verify if the path is valid

    @property
    def processable_file_names(self):
        return self._processable_file_names

    @processable_file_names.setter
    def processable_file_names(self, processable_file_names):
        self._processable_file_names = processable_file_names

    @property
    def processable_directories(self):
        return self._processable_directories

    @processable_directories.setter
    def processable_directories(self, processable_directories):
        self._processable_directories = processable_directories
