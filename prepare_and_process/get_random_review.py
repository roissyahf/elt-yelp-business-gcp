import json
import random

# input & output file
input_file = "yelp_review_splitted_10_random/split_review_70.json"
output_file = "yelp_sample_review/yelp_split_review_70_sample2_20k.json"

# number of samples you want (20k out of 70k)
n_samples = 20000

# First pass: count total lines
with open(input_file, "r", encoding="utf-8") as f:
    total_lines = sum(1 for _ in f)

# pick random line numbers to sample
sample_indices = set(random.sample(range(total_lines), n_samples))

sampled = []
unique_business_ids = set()

# Second pass: collect sampled JSONs
with open(input_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as out:
    for i, line in enumerate(f):
        if i in sample_indices:
            data = json.loads(line)
            sampled.append(data)
            unique_business_ids.add(data.get("business_id"))
            out.write(json.dumps(data) + "\n")

print(f"✅ Sampled {len(sampled)} reviews")
print(f"✅ Unique business_id: {len(unique_business_ids)}")