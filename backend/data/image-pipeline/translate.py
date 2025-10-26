import re
import json

def parse_meme_clusters(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split into main fields (DESCRIPTION, HUMOR, TOPIC, etc.)
    field_sections = re.split(r"=== FIELD: (.*?) ===", text)[1:]  # skip header
    result = {}

    for i in range(0, len(field_sections), 2):
        field_name = field_sections[i].strip()
        field_text = field_sections[i + 1]

        clusters = re.split(r"📁 Cluster (\d+) — \d+ memes", field_text)[1:]
        clusters_dict = {}

        for j in range(0, len(clusters), 2):
            cluster_num = clusters[j]
            cluster_text = clusters[j + 1]

            # Extract individual memes
            memes = re.findall(r"• (.*?): (.*)", cluster_text)
            clusters_dict[cluster_num] = [
                {"file": m[0].strip(), "description": m[1].strip()}
                for m in memes
            ]

        result[field_name] = clusters_dict

    return result


if __name__ == "__main__":
    input_file = "meme_clusters.txt"
    output_file = "meme_clusters.json"

    parsed_data = parse_meme_clusters(input_file)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Converted {input_file} → {output_file}")
