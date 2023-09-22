import os
import argparse
from pathlib import Path

Script_path = Path(__file__).resolve()
ROOT = Script_path.parents[0]
print(ROOT)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root_path", type=str, help="Directory of the root")
    parser.add_argument("-f", "--folders_path", type=str, help="Directory of the folders")
    args = parser.parse_args()

    folder_path: object = args.folders_path
    folders = os.listdir(folder_path)
    # print(folders)

    Folder_index = 1


    for old_folder_name in folders:
        new_name = old_folder_name.replace(f"{old_folder_name}", 'P'+ str(Folder_index))
        os.rename(os.path.join(folder_path, old_folder_name),os.path.join(folder_path, new_name))
        Folder_index += 1

    new_folders = os.listdir(folder_path)

    for folder in new_folders:
        video_index = 1
        video_path = folder_path + folder
        Videos = os.listdir(video_path)
        for old_video_name in Videos:
            new_vid_name = old_video_name.replace(f"{old_video_name}", str(folder) + "_" + str(video_index))
            os.rename(os.path.join(video_path, old_video_name), os.path.join(video_path, new_vid_name))
            video_index += 1