import os
import subprocess
from modules.artifact_extraction import ArtifactExtractor

class MftExtractor(ArtifactExtractor):
    def __init__(self, output_dir, file_path):
        self.output_dir = output_dir
        self.file_path = file_path
        self.mft_output_dir =  os.path.join(output_dir, "mftextract")
        try:
            os.mkdir(self.output_dir_dir)
        except FileExistsError:
            print("Error: File Exists Error")
        self.extract_mft(file_path)

    def extract_mft(self, file_path):
        metadataByLine = []
        offsetDatas = []
        theOffset = 2048
        fileRaw = os.path.join(self.output_dir, "mft.raw")

        try:
            mmlsDatas = subprocess.check_output(['mmls', 'disk.E01'])
        except subprocess.CalledProcessError as e:
            print("Error with mmls: CalledProcessError")
        metadataByLine = mmlsDatas.decode().split('\r\n')
        for data in metadataByLine:
            if ('-------' in data):
                offsetDatas  = data.split()
                break
        theOffset = int(offsetDatas[-2])
        try:
            #TODO check the output file
            #TODO check for the offset if it s good
            os.system('icat -o ' + f'{theOffset} ' + f'{file_path} ' +  '0 > '+ f'{fileRaw}')
            #subprocess.call(['icat', '-o', f'{theOffset}', 'disk.E01', '0'])
        except:
            print("Error with icat ") 

    
    def mft_to_csv(self):
        pass