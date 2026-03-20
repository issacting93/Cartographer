from datasets import load_dataset
try:
    print("Trying to load ShenLab/PISCES...")
    ds = load_dataset("ShenLab/PISCES", split="train", streaming=True)
    print("Success! It exists.")
    print("Sample:", next(iter(ds)))
except Exception as e:
    print("Failed to load ShenLab/PISCES:", e)

try:
    print("\nTrying to load MPISCES (maybe typo?)...")
    ds = load_dataset("ShenLab/MPISCES", split="train", streaming=True)
    print("Success!")
except:
    pass
