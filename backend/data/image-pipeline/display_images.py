import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# === CONFIG ===
MEME_DIR = "all_memes"

cluster8_files = [
    "memes_1ofhsqm.jpeg",
    "196_1of9ubp.jpeg",
    "AdviceAnimals_1ofd731.jpeg",
    "AdviceAnimals_1ofefpx.png",
    "AdviceAnimals_1ofsglu.png",
    "196_1of6y78.jpeg",
    "196_1ofatcr.jpeg",
    "starterpacks_1ofov7t.jpeg",
    "HistoryMemes_1ofbiby.jpeg",
    "AdviceAnimals_1ofxmq1.jpeg",
    "AdviceAnimals_1ofcu3z.jpeg",
    "196_1ofcf1i.jpeg",
    "memes_1ofm1c1.jpeg",
    "196_1of7gy4.jpeg",
]

# === Filter existing files ===
existing = [f for f in cluster8_files if os.path.exists(os.path.join(MEME_DIR, f))]
if not existing:
    print("⚠️  No images found in 'all_memes' — check your folder or filenames.")
    exit()

# === Layout ===
cols = 5
rows = (len(existing) + cols - 1) // cols

fig, axes = plt.subplots(rows, cols, figsize=(16, rows * 3))
axes = axes.flatten()

for ax, fname in zip(axes, existing):
    img_path = os.path.join(MEME_DIR, fname)
    img = mpimg.imread(img_path)
    ax.imshow(img)
    ax.set_title(fname, fontsize=8)
    ax.axis("off")

# Hide any unused cells
for ax in axes[len(existing):]:
    ax.axis("off")

plt.suptitle("Cluster 8 — Political, Economic, and Social Commentary Memes", fontsize=14)
plt.tight_layout()
plt.show()
