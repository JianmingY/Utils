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
    folders = os.listdir(folder_path)
    # print(folders)

    Folder_index = 1

    folder_dic = {"Old_folder": [],
                  "New_folder": []}
    for old_folder_name in folders:
        if not ".csv" in old_folder_name:
            folder_dic["Old_folder"].append(old_folder_name)
            new_name = old_folder_name.replace(f"{old_folder_name}", 'P'+ str(Folder_index))
            folder_dic["New_folder"].append(new_name)
            os.rename(os.path.join(folder_path, old_folder_name),os.path.join(folder_path, new_name))
            Folder_index += 1

    new_folders = os.listdir(folder_path)
    new_folders = [x for x in new_folders if not ".csv" in x]

    video_dic = {"Old_video": [],
                 "New_video": []}

    for folder in new_folders:
        video_index = 1
        video_path = folder_path + folder
        Videos = os.listdir(video_path)
        Videos = [x for x in Videos if ".MP4" in x]
        for old_video_name in Videos:
            video_dic["Old_video"].append(old_video_name)
            new_vid_name = old_video_name.replace(f"{old_video_name}", str(folder) + "_" + str(video_index) + ".MP4")
            video_dic["New_video"].append(new_vid_name)
            os.rename(os.path.join(video_path, old_video_name), os.path.join(video_path, new_vid_name))
            video_index += 1

    folder_df = pd.DataFrame(folder_dic)
    video_df = pd.DataFrame(video_dic)

    folder_df.to_csv(folder_path + "Folder_Reference.csv")
    video_df.to_csv(folder_path + "Video_Reference.csv")

    print("Files have been renamed in order and changes were saved.")