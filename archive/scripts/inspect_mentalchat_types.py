from datasets import load_dataset

def main():
    ds = load_dataset("ShenLab/MentalChat16K", split="train", streaming=True)
    
    all_keys = set()
    types = {}
    
    print("Scanning first 2000 rows...")
    for i, row in enumerate(ds):
        if i >= 2000: break
        
        all_keys.update(row.keys())
        
        # Check types of values
        for k, v in row.items():
            t = type(v).__name__
            if k not in types: types[k] = set()
            types[k].add(t)
            
        # Check for "pisces" string in any value
        row_str = str(row).lower()
        if "pisces" in row_str:
            print(f"Found 'pisces' in row {i}!")
            print(row)
            return

    print("Keys found:", all_keys)
    print("Types found:", types)
    print("Scanning finished. 'pisces' not found in first 2000 rows text.")

if __name__ == "__main__":
    main()
