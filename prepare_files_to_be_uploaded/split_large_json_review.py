# Code subject to https://github.com/ankitbansal6/end_to_end_data_analytics_project/
# Original code author: Ankit Bansal
# This code splits a large JSON file (with one JSON object per line) into multiple smaller files (100)

import os

input_file = "yelp_dataset/yelp_academic_dataset_review.json"  # 5GB JSON file
output_prefix = "split_review_"  # Prefix for output files
output_directory = "yelp_review_splitted" # Using absolute path
num_files = 100  # Number of files to split into, total lines is around 6.9 mio

# Count total lines (objects) in the file
with open(input_file, "r" , encoding="utf8") as f:
    total_lines = sum(1 for _ in f)  

lines_per_file = total_lines // num_files  # Lines per split file

print(f"Total lines: {total_lines}, Lines per file: {lines_per_file}")

# Create directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Now split into multiple smaller files
with open(input_file, "r" , encoding="utf8") as f:
    for i in range(num_files):
        output_filename = f"{output_prefix}{i+1}.json"
        full_file_path = os.path.join(output_directory, output_filename)

        with open(full_file_path, "w", encoding="utf8" ) as out_file:
            for j in range(lines_per_file):
                line = f.readline()
                if not line:
                    break  # Stop if file ends early
                out_file.write(line)

print("✅ JSON file successfully split into smaller parts!")