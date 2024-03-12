import pickle
from typing import Any
import requests 


def save_data(data, file_name: str):
    with open(file_name, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_data(file_name: str):
    with open(file_name, "rb") as f:
        try:
            data = pickle.load(f)
        except EOFError:
            return None
    return data


class PermanentData:
    def __init__(self) -> None:
        self.all_data = {}

    def set(self, file_name: str, data: Any) -> None:
        self.all_data[file_name] = data

    def get(self, file_name: str) -> Any:
        return self.all_data[file_name] 
    
    def load(self, *file_names):
        for file_name in file_names:
            try:
                self.all_data[file_name] = load_data(file_name)
            except (FileNotFoundError):
                save_data(self.get(file_name), file_name)

    def save(self) -> None:
        for file_name, data in self.all_data.items():

            save_data(data, file_name)

def load_from_url(url: str) -> str:
    r = requests.get(url) 
    content = r.text 

    return content

    