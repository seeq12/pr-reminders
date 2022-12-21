import os
import pathlib
from typing import TypedDict


class QueryRequest(TypedDict):
    query: str
    variables: dict


def load_query(name: str) -> str:
    module_directory = pathlib.Path(os.path.realpath(__file__)).parent
    with open(module_directory / name) as query_file:
        return query_file.read()
