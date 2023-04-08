class ArtifactExtractor:
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
        if not self._processable_file_names :
            raise NotImplementedError("Subclasses must implement processable_file_names")
        return self._processable_file_names
    
    @processable_file_names.setter
    def processable_file_names(self, processable_file_names):
        self._processable_file_names = processable_file_names

    @property
    def processable_directories(self):
        if not self._processable_directories:
            raise NotImplementedError("Subclasses must implement processable_directory")        
        return self.processable_directories
    
    @processable_directories.setter
    def processable_directories(self, processable_directories):
        self._processable_directories = processable_directories