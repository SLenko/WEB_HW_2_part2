from collections import UserDict
from datetime import datetime
import json
from abc import ABC, abstractmethod

class UserInterface(ABC):
    @abstractmethod
    def display_options(self):
        pass

    @abstractmethod
    def get_user_choice(self):
        pass

    @abstractmethod
    def display_message(self, message):
        pass

    @abstractmethod
    def get_user_input(self, prompt):
        pass


class ConsoleInterface(UserInterface):
    def display_options(self):
        print("\nOptions:")
        print("1. Add contact")
        print("2. Delete contact")
        print("3. Search contacts")
        print("4. Show all contacts")
        print("5. Contacts birthday")
        print("6. Exit")

    def get_user_choice(self):
        return input("Enter your choice (1-6): ")

    def display_message(self, message):
        print(message)

    def get_user_input(self, prompt):
        return input(prompt)


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self):
        return str(self.value)
    
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Name(Field):
    pass


class Birthday(Field):
    @Field.value.setter
    def value(self, value: str):
        try:
            self._Field__value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid birthday format. Use YYYY-MM-DD")


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @Field.value.setter
    def value(self, value):
        if value.isdigit() and len(value) == 10:
            self._Field__value = value
        else:
            raise ValueError ("Invalid phone number format. Phone not added.")
    

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if not any(p.value == old_phone for p in self.phones):
            raise ValueError("Phone number not found.")
        
        self.remove_phone(old_phone)
        self.add_phone(new_phone)
        
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def days_to_birthday(self):
        if not self.birthday:
            return None
        
        today = datetime.today()
        next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)

        if today > next_birthday:
            next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)

        days_left = (next_birthday - today).days
        return days_left


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, query):
        results = []
        for name, record in self.data.items():
            if query.lower() in name.lower():
                results.append(record)
            else:
                for phone in record.phones:
                    if query in phone.value:
                        results.append(record)
                        break
        return results

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, item_number):
        counter = 0
        result = ''
        for item, record in self.data.items():
            result += f'{item}: {record}'
            counter += 1
            if counter >= item_number:
                yield result
                counter = 0
                result = ''

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            data_to_save = {
                'records': {name: {'phones': [phone.value for phone in record.phones],
                                   'birthday': str(record.birthday.value) if record.birthday else None}
                            for name, record in self.data.items()}
            }
            json.dump(data_to_save, file)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            for name, record_data in data['records'].items():
                record = Record(name, birthday=record_data['birthday'])
                for phone in record_data['phones']:
                    record.add_phone(phone)
                self.add_record(record)

    def add_contact(self, user_interface):
        name = user_interface.get_user_input("Enter contact name: ")
        birthday = user_interface.get_user_input("Enter birthday (YYYY-MM-DD): ")
        record = Record(name, birthday)
    
        phone_count = user_interface.get_user_input("Enter the number of phone numbers to add: ")
        record.add_phone(phone_count)
    
        self.add_record(record)
        user_interface.display_message("Contact added successfully.")

    def delete_contact(self, user_interface):
        name = user_interface.get_user_input("Enter contact name to delete: ")
        self.delete(name)
        user_interface.display_message("Contact deleted successfully.")

    def search_contacts(self, user_interface):
        query = user_interface.get_user_input("Enter name or phone number to search: ")
        results = self.find(query)
    
        if results:
            user_interface.display_message("Search results:")
            for result in results:
                print(result)
        else:
            user_interface.display_message("No matching contacts found.")

    def show_all_contacts(self, user_interface):
        if self.data:
            user_interface.display_message("\nAll contacts:")
            for record in self.data.values():
                print(record)

    def show_all_contacts_with_birthdays(self, user_interface):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.values():
            days_left = record.days_to_birthday()
            if days_left is not None:  
                upcoming_birthdays.append((record, days_left))

        if upcoming_birthdays:
            user_interface.display_message("\nUpcoming birthdays:")
            for record, days_left in upcoming_birthdays:
                print(f"{record.name.value}: {record.birthday.value} (in {days_left} days)")

def main():
    address_book = AddressBook()
    console_interface = ConsoleInterface()

    try:
        address_book.load_from_file('address_book.json')
        console_interface.display_message("Address book loaded successfully.")
    except FileNotFoundError:
        console_interface.display_message("No existing address book found.")

    while True:
        console_interface.display_options()
        choice = console_interface.get_user_choice()

        if choice == '1':
            address_book.add_contact(console_interface)
        elif choice == '2':
            address_book.delete_contact(console_interface)
        elif choice == '3':
            address_book.search_contacts(console_interface)
        elif choice == '4':
            address_book.show_all_contacts(console_interface)
        elif choice == '5':
            address_book.show_all_contacts_with_birthdays(console_interface)
        elif choice == '6':
            address_book.save_to_file('address_book.json')
            console_interface.display_message("Address book saved. Exiting...")
            break
        else:
            console_interface.display_message("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()
