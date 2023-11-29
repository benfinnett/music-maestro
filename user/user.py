import os
import json

class User:
    '''
    User class to handle song performance storing.
    '''
    def __init__(self) -> None:
        self.data_file_path: str = ''
        self.logged_in = False

    def _load_data(self) -> None:
        '''
        Load user data from a JSON file.
        
        Raises:
            Exception: If the file path is not provided.
        '''
        if not self.data_file_path:
            raise Exception("Unable to load user data as the file path has not been provided.")
        
        with open(self.data_file_path, 'r') as file:
            self.data: dict[str, str | int] = json.load(file)

    def validate(self, username: str, password: str) -> str | None:
        '''
        Validate a user's credentials and load their data if valid.
        
        Args:
            username (str): The username to validate.
            password (str): The password to validate.
        
        Returns:
            str | None: An error message if validation fails, or None if successful.
        '''
        if not username or not password:
            return 'Both fields must be filled in.'
        
        directory = [[files, root] for root, _, files in os.walk('.\\assets\\users\\')]
        if len(directory) == 1 and not directory[0][0]:
            return 'User does not exist.'

        for file in directory[0][0]:
            if username in file:
                self.data_file_path = directory[0][1] + file
                self._load_data()

                if password == self.data['password']:
                    self.username = username
                    self.logged_in = True
                    return
                else:
                    self.data_file_path = ''
                    self.data = {}
                    return 'Invalid password.'
        return 'User does not exist.'

    def create(self, username: str, password: str) -> str | None:
        '''
        Create a new user with the provided username and password.
        
        Args:
            username (str): The username to create.
            password (str): The password to set for the user.
        
        Returns:
            str | None: An error message if creation fails, or None if successful.
        '''
        if not username or not password:
            return 'Both fields must be filled in.'
        
        error = self.validate(username, password)
        if error != 'User does not exist.':
            return 'User already exists.'
        
        self.data_file_path = f'.\\assets\\users\\{username}.json'
        self.username = username
        self.logged_in = True
        self.save({'password': password})

    def save(self, data: dict[str, str | int]) -> None:
        '''
        Save user data to a JSON file.
        
        Args:
            data (dict): The user data to be saved.
        
        Raises:
            Exception: If the file path is not provided.
        '''
        self.data = data

        if not self.data_file_path:
            raise Exception("Unable to save user data as the file path has not been provided.")
        
        with open(self.data_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def remove(self) -> None:
        '''
        Remove the user's data file.
        
        Raises:
            ValueError: If the file path is not provided.
        '''
        if not self.data_file_path:
            raise ValueError("Unable to remove user data as the file path has not been provided.")
        
        self.logged_in = False
        os.remove(self.data_file_path)

    def get_data(self) -> dict[str, str | int]:
        '''
        Get the user's data.
        
        Returns:
            dict: The user's data if available, or an empty dictionary if the file path is not stored.
        '''
        if self.data_file_path:
            self._load_data()
            return self.data
        else:
            return {}

    def get_username(self) -> str | None:
        '''
        Get the username associated with the user's data.
        
        Returns:
            str | None: The username if available, or None if the file path is not stored.
        '''
        if self.data_file_path:
            return self.username
        else:
            return None