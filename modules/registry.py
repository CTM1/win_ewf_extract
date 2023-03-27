import pytsk
import csv

def extract(ewf_file, keys=None, output_dir="./output"):
    img = pytsk3.Img_Info(ewf_file)
    reg = pytsk3.Registry_Info(img)

    if keys is None:
        keys = [key.path() for key in reg.recurse_subkeys()]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
    
        writer.writerow(["Registry Key", "Value", "Type", "Created At", "Modified At", "Deleted At"])

        for key in registry_keys:
            value = key.value()        
            writer.writerow([key.path(), value.data(), value.type(), key.info.crtime, key.info.mtime, key.info.dtime])