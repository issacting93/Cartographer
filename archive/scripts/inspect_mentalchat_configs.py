from datasets import get_dataset_config_names
try:
    configs = get_dataset_config_names("ShenLab/MentalChat16K")
    print("Configs:", configs)
except Exception as e:
    print("Error getting configs:", e)
    print("Assuming 'default' config.")
