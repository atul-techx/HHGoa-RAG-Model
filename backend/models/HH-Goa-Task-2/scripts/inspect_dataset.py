from datasets import load_dataset

print("Loading MSMARCO-XI schema...")

dataset = load_dataset(
    "ai4bharat/MSMARCO-XI",
    split="train",
    streaming=True
)

print("\nDataset loaded successfully!")

print("\nColumns:")
for column in dataset.column_names:
    print(" -", column)

print("\nDataset features:")
print(dataset.features)

print("\nInspecting only metadata...")
print("No full record will be loaded.")