import json

# for initial: use split_review_6 until split_review_53
# paths
sampled_reviews_file = "yelp_sample/yelp_split_review_53_sample_30k.json"      # from your previous step
business_source_file = "yelp_dataset/yelp_academic_dataset_business.json"       # the business info file you mentioned
matched_business_out = "yelp_sample_business/yelp_business_split_review_53_sample_30k.json"

# 1) collect unique business_ids from the sampled reviews
business_ids = set()
with open(sampled_reviews_file, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        obj = json.loads(line)
        bid = obj.get("business_id")
        if bid:
            business_ids.add(bid)

# 2) stream the business file and write only the matching records
found = set()
written = 0

with open(business_source_file, "r", encoding="utf-8") as src, \
     open(matched_business_out, "w", encoding="utf-8") as out:

    for line in src:
        if not line.strip():
            continue
        try:
            bobj = json.loads(line)
        except json.JSONDecodeError:
            # If your business file is a single large JSON array (rare for Yelp),
            # this line-by-line approach won't work. In that case, consider using `ijson`
            # for true streaming. But for typical Yelp NDJSON, this is correct.
            raise

        bid = bobj.get("business_id")
        if bid and bid in business_ids and bid not in found:
            out.write(json.dumps(bobj, ensure_ascii=False) + "\n")
            found.add(bid)
            written += 1

# 3) print summary
print(f"✅ Sampled reviews: {len(business_ids)} unique business_id")
print(f"✅ Matched businesses written: {written}")
missing = business_ids - found
print(f"⚠️ Not found in business file: {len(missing)}")