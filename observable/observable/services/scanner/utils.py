import os
from typing import (Iterator,
                    Dict,
                    Tuple)

from observable.types import StateDiffType


def states_diff_stream(old_state: Dict[str, int],
                       new_state: Dict[str, int]
                       ) -> Iterator[Tuple[str, StateDiffType]]:
    old_state_files_paths = set(old_state)
    new_state_files_paths = set(new_state)
    modified_files_paths = old_state_files_paths & new_state_files_paths
    created_files_paths = new_state_files_paths - modified_files_paths
    removed_files_paths = old_state_files_paths - modified_files_paths

    for file_path in created_files_paths:
        yield file_path, {'size': new_state[file_path],
                          'type': 'created'}

    for file_path in removed_files_paths:
        yield file_path, {'size': 0,
                          'type': 'removed'}

    for file_path in modified_files_paths:
        new_size = new_state[file_path]
        is_modified = new_size - old_state[file_path]
        if is_modified:
            yield file_path, {'size': new_size,
                              'type': 'modified'}


def file_size(path: str) -> int:
    file_statistics = os.stat(path,
                              follow_symlinks=False)
    return file_statistics.st_size


def files_paths(directory_path: str) -> Iterator[str]:
    for root, _, files_names in os.walk(directory_path):
        for file_name in files_names:
            yield os.path.join(root, file_name)
