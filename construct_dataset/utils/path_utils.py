"""
@File        :   path_utils.py
@Description :   utility functions for getting file path.
@Time        :   2024/10/30
"""

import os

def get_all_sub_folders(root_folder):
    """
    Get all sub-folders in the given root folder.
    Args:
        root_folder (str): The path to the root folder.
    Returns:
        list: A list of paths to all sub-folders in the root folder.
    """
    all_folders = []
    for folder in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder)
        if os.path.isdir(folder_path):
            all_folders.append(folder_path)
    return all_folders