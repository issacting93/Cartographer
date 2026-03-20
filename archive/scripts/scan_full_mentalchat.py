from datasets import load_dataset, get_dataset_split_names

def main():
    try:
        splits = get_dataset_split_names("ShenLab/MentalChat16K")
        print("Splits:", splits)
    except Exception as e:
        print("Error getting splits:", e)
        splits = ['train']

    for split in splits:
        print(f"\nScanning split: {split}...")
        ds = load_dataset("ShenLab/MentalChat16K", split=split) # Load all to memory, it's small
        print(f"Total rows: {len(ds)}")
        
        found = 0
        for i, row in enumerate(ds):
            row_str = str(row).lower()
            if "pisces" in row_str:
                if found < 3:
                     print(f"Found 'pisces' in row {i}:")
                     print(row)
                found += 1
        
        print(f"Total 'pisces' rows in {split}: {found}")

if __name__ == "__main__":
    main()
