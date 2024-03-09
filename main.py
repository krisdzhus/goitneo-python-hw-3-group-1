from collections import UserDict
from datetime import datetime, timedelta

class PhoneValidationError(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise PhoneValidationError("Please enter a valid number.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        today = datetime.now().date()
        monday = (today - timedelta(days=today.weekday()))
        next_monday = monday + timedelta(weeks=1)
        end_of_next_week = next_monday + timedelta(days=7)

        birthday_dict = {}
        for name, record in self.data.items():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, '%d.%m.%Y').date()
                birthday_this_year = birthday.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = record.birthday.value.replace(year=today.year + 1)
                if next_monday <= birthday_this_year < end_of_next_week:
                    weekday = birthday_this_year.strftime('%A')
                    if weekday == "Saturday" or weekday == "Sunday":
                        weekday = 'Monday'
                    if weekday not in birthday_dict:
                        birthday_dict[weekday] = []
                    birthday_dict[weekday].append(name)
        return birthday_dict

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PhoneValidationError as e:
            return str(e)
        except ValueError as v:
            return f"Give me name and phone please."
        except KeyError as k:
            return f"Give me the right name, please."
        except IndexError as i:
            return f"Give me the right index, please."
        
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

def change_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.phones = [Phone(phone)]
        return "Contact updated"
    else:
        raise KeyError("Contact not found.")

def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return record.phones[0].value
    else:
        raise KeyError("Contact not found.")

def show_all(book):
    contacts = []
    for record in book.data.values():
        contacts.append((record.name.value, [phone.value for phone in record.phones]))
    return contacts

def add_birthday_handler(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)  # Виправлено
        print("Birthday added.")
    else:
        print("Contact not found")


def show_birthday_handler(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        print(f"{name}'s birthday: {record.birthday.value}")
    else:
        print("Birthday not found")

def birthdays_handler(book):
    birthdays_this_week = book.get_birthdays_per_week()
    if birthdays_this_week:
        print("Birthdays coming up this week:")
        for name in birthdays_this_week:
            print(name)
    else:
        print("No birthdays coming up this week")

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            add_birthday_handler(args, book)
        elif command == "show-birthday":
            show_birthday_handler(args, book)
        elif command == "birthdays":
            birthdays_handler(book)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()