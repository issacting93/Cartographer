from datasets import load_dataset
print("Loading dataset...")
ds = load_dataset('ShenLab/MentalChat16K', split='train', streaming=True)
row = next(iter(ds))
print("Sample row keys:", row.keys())
print("Sample row:", row)
