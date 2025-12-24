import numpy as np
import os
import json
import shutil
import objaverse

def load_json(fname):
	f = open(fname)
	content = json.load(f)
	f.close()
	return content

def write_json(graph, output_dir):
	json_graph = json.dumps(graph, indent=4)
	with open(output_dir, "w") as outfile:
		outfile.write(json_graph)
	outfile.close()