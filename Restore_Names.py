import os
import argparse
from pathlib import Path
import pandas as pd

Script_path = Path(__file__).resolve()
ROOT = Script_path.parents[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folders_path", type=str, help="Directory of the folders")
    args = parser.parse_args()

    folder_path = args.folders_path

    folder_reference_path = os.path.join(folder_path, "Folder_Reference.csv")
    video_reference_path = os.path.join(folder_path, "Video_Reference.csv")

    folder_df = pd.read_csv(folder_reference_path)
    video_df = pd.read_csv(video_reference_path)
    for index, row in video_df.iterrows():
        old_name = row["Old_video"]
        new_name = row["New_video"]

        folder_name = new_name.split("_")[0]

        os.rename(os.path.join(folder_path, folder_name, new_name),os.path.join(folder_path, folder_name, old_name))


    for index, row in folder_df.iterrows():
        old_name = row["Old_folder"]
        new_name = row["New_folder"]
        os.rename(os.path.join(folder_path, new_name),os.path.join(folder_path, old_name))


    print("Files have been renamed back to their original name!")