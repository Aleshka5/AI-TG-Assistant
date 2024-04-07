import os
import glob

def get_dataset_path(new = False):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    if new:
        dataset_path = os.path.join(current_dir, "my_database.db")
        return dataset_path

    else:
        dataset_file = glob.glob(os.path.join(current_dir, "*.db"))

        if len(dataset_file) < 1:
            return None
        if len(dataset_file) > 1:
            raise ValueError("Exactly one file should be present in the directory.")

        dataset_path = dataset_file[0]
        return dataset_path