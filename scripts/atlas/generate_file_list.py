import glob
import os
import json

graph_dir = "data/atlas_canonical/graphs"
files = [os.path.basename(f) for f in glob.glob(os.path.join(graph_dir, "*.json"))]
files.sort()

output_path = "scripts/atlas/file_list.js"
with open(output_path, "w") as f:
    f.write("const files = " + json.dumps(files, indent=4) + ";")

print(f"Generated {output_path} with {len(files)} files.")
