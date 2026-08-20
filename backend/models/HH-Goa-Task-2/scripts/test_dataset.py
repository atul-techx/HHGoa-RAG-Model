from datasets import load_dataset

print("Loading MSMARCO-XI dataset...")

dataset = load_dataset("ai4bharat/MSMARCO-XI")

print("\nDataset loaded successfully!")
print(dataset)

print("\nDataset splits:")
print(dataset.keys())

for split in dataset.keys():
    print(f"\n===== {split} =====")

    print("Columns:")
    print(dataset[split].column_names)

    print("\nFirst record:")
    print(dataset[split][0])