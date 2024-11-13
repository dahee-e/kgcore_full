import os
import csv
import argparse
import utils



# Argument parser for command-line arguments
parser = argparse.ArgumentParser(description="Extract data from EPA and NPA files and save to CSV")
parser.add_argument("--directory", help="Path to the directory containing files"
                    , default='./datasets/')
parser.add_argument("--output", help="Output CSV file name", default='summary.csv')
args = parser.parse_args()

input_file = args.directory + 'network.hyp'
hypergraph, E = utils.load_hypergraph(input_file)

# Define the output CSV file path
output_csv_path = os.path.join(args.directory, args.output)

# Prepare data list for CSV rows
data = []

# Loop through each file in the directory
for filename in os.listdir(args.directory):
    # Process only files matching the pattern
    if filename.startswith("EPA") or filename.startswith("NPA"):
        file_path = os.path.join(args.directory, filename)

        # Extract algorithm, k, and g from the filename
        f = filename.split("_")[0]  # Remove the extension
        algorithm = filename.split("_")[0]  # "EPA" or "NPA"
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

            average_degree = 0
            average_cardinality = 0
            if num_of_nodes == 0 or runtime is None:
                continue
            average_cardinality = 0
            induced_subhypergraph = utils.get_induced_subhypergraph(hypergraph, set(nodes))
            for v in nodes:
                average_cardinality = average_cardinality + utils.degree(hypergraph, v)
            average_cardinality = average_cardinality / len(nodes)
            average_degree = 0
            for v in nodes:
                average_degree = average_degree + utils.hyperedges_count(hypergraph, v)
            average_degree = average_degree / len(nodes)

            # Append extracted data to list
            data.append({
                "algorithm": algorithm,
                "k": k,
                "g": g,
                "# of nodes": num_of_nodes,
                "runtime": runtime,
                "average_degree": average_degree,
                "average_cardinality": average_cardinality
                # ,"nodes": nodes
            })


# Write the data to a CSV file
with open(output_csv_path, 'w', newline='') as csvfile:
    fieldnames = ["algorithm", "k", "g", "# of nodes", "runtime","average_degree","average_cardinality"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in data:
        # Join nodes list as a space-separated string for CSV
        # row["nodes"] = ' '.join(map(str, row["nodes"]))
        writer.writerow(row)

print(f"Data successfully written to {output_csv_path}")