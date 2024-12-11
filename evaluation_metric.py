import os
import csv
import argparse
import utils
import time
import hypernetx.algorithms.hypergraph_modularity as hmod

# Argument parser for command-line arguments
parser = argparse.ArgumentParser(description="Extract data from EPA and NPA files and save to CSV")
parser.add_argument("--directory", help="Path to the directory containing files"
                    , default='./datasets/real/gowalla/')
parser.add_argument("--output", help="Output CSV file name", default='summary_modify.csv')
args = parser.parse_args()

input_file = args.directory + 'network.hyp'
hypergraph, E = utils.load_hypergraph(input_file)
output_f = args.directory.split('/')[-2]+'_summary.csv'
# Define the output CSV file path
output_csv_path = os.path.join(args.directory, output_f)

# Prepare data dictionary for EPA data
epa_data = {}

# Loop through each file in the directory
for filename in os.listdir(args.directory):
    # Process only files starting with "EPA"
    if filename.startswith("EPA"):
        file_path = os.path.join(args.directory, filename)

        # Extract algorithm, k, and g from the filename
        algorithm = "EPA"
        k = int(filename.split("_")[1])
        g = int(filename.split("_")[2])

        # Read the file to get node count, runtime, and nodes
        with open(file_path, 'r') as file:
            lines = file.readlines()

            # Initialize variables
            num_of_nodes = None
            runtime = None
            nodes = []

            for line in lines:
                # Extract number of nodes
                if line.startswith("Num of nodes:"):
                    num_of_nodes = int(line.split(":")[1].strip())

                # Extract runtime
                elif line.startswith("Run Time:"):
                    runtime = float(line.split(":")[1].strip())

                # Extract nodes list
                elif line.startswith("Nodes:"):
                    nodes = line.split(":")[1].strip().split()
                    nodes = [int(node) for node in nodes]  # Convert nodes to integer list
            average_cardinality = 0
            average_degree = 0
            if num_of_nodes == 0 or runtime is None:
                continue


            # average_cardinality = utils.edge_count(nodes,E)
            # average_cardinality = average_cardinality / len(nodes)
            #
            #
            # for v in nodes:
            #     average_degree += utils.hyperedges_count(hypergraph, v)
            # average_degree = average_degree / len(nodes)


            # Store EPA data in a dictionary with (k, g) as the key
            epa_data[(k, g)] = {
                "algorithm": algorithm,
                "k": k,
                "g": g,
                "# of nodes": num_of_nodes,
                "runtime": runtime,
                "average_degree": average_degree,
                "average_cardinality": average_cardinality,  # Assuming average_cardinality is 0 as per original code
                "dataset": args.directory.split('/')[-2]
            }

# Now process NPA files
for filename in os.listdir(args.directory):
    if filename.startswith("NPA"):
        file_path = os.path.join(args.directory, filename)

        # Extract algorithm, k, and g from the filename
        algorithm = "NPA"
        k = int(filename.split("_")[1])
        g = int(filename.split("_")[2])

        # Check if corresponding EPA data exists
        if (k, g) in epa_data:
            # Read the file to get runtime
            with open(file_path, 'r') as file:
                lines = file.readlines()

                # Initialize variables
                runtime = None

                for line in lines:
                    # Extract runtime
                    if line.startswith("Run Time:"):
                        runtime = float(line.split(":")[1].strip())
                        break

            if runtime is None:
                continue

            # Use average_degree and average_cardinality from EPA
            epa_record = epa_data[(k, g)]
            epa_data[(k, g, 'NPA')] = {
                "algorithm": algorithm,
                "k": k,
                "g": g,
                "# of nodes": epa_record["# of nodes"],
                "runtime": runtime,
                # "average_degree": epa_record["average_degree"],
                # "average_cardinality": epa_record["average_cardinality"],
                "dataset": epa_record["dataset"]
            }

# Combine EPA and NPA data
data = list(epa_data.values())

# Write the data to a CSV file
with open(output_csv_path, 'w', newline='') as csvfile:
    fieldnames = ["algorithm", "k", "g", "# of nodes", "runtime", "average_degree", "average_cardinality", "dataset"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in data:
        writer.writerow(row)

print(f"Data successfully written to {output_csv_path}")