import pytsk3

def extract(ewf_file, keys=None):
    # Open the Encase file
    img = pytsk3.Img_Info(ewf_file)

    # Open the Windows Registry hive
    reg = pytsk3.Registry_Info(img)

    if keys is None:
        keys = [key.path() for key in reg.recurse_subkeys()]
    
    for key in keys:
        print(key)