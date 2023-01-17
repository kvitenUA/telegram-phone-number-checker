#!/usr/local/bin/python3
from telethon import TelegramClient, errors, events, sync
from telethon.tl.types import InputPhoneContact
from telethon import functions, types
from dotenv import load_dotenv
import argparse
import os
from getpass import getpass


load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

def get_names(phone_number):    
    try:
        contact = InputPhoneContact(client_id = 0, phone = phone_number, first_name="", last_name="")
        contacts = client(functions.contacts.ImportContactsRequest([contact]))
        username = contacts.to_dict()['users'][0]['username']
        if not username:
            print(f"https://t.me/+{phone_number}") # return telegram link to user based on phone number
            client(functions.contacts.DeleteContactsRequest(id=[contacts.users[0]]))
            return (f"https://t.me/+{phone_number}")
        else:
            print(f"https://t.me/+{phone_number}")
            client(functions.contacts.DeleteContactsRequest(id=[contacts.users[0]]))
            return
    except IndexError as e:
        return f'NO ACCOUNT'
    except TypeError as e:
        return f"https://t.me/+{phone_number}"
    except:
        raise

def user_validator(phone_numbers: list):
    '''
    The function uses the get_api_response function to first check if the user exists and if it does, then it returns the first user name and the last user name.
    '''
    result = {}
    for phone in phones:
        api_res = get_names(phone)
        result[phone] = api_res

    return result

if __name__ == '__main__':
    # parse argument
    parser = argparse.ArgumentParser(description='Check to see if a phone number is a valid Telegram account')
    parser.add_argument('-i', '--input', dest='input_file_path', help='Path to an optional telephone list .txt file to be used as input')
    parser.add_argument('-o', '--output', dest='output_filename',
                        help='If present, saves the output to a CSV file with the given filename')
    args = parser.parse_args()

    # Connect
    client = TelegramClient(PHONE_NUMBER, API_ID, API_HASH)
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(PHONE_NUMBER)
        try:
            client.sign_in(PHONE_NUMBER, input('Enter the code (sent on telegram): '))
        except errors.SessionPasswordNeededError:
            pw = getpass('Two-Step Verification enabled. Please enter your account password: ')
            client.sign_in(password=pw)

    # get input from file if the argument was used, if not, get them from the user input
    input_phones = []
    if not args.input_file_path:
        input_phones = input("Phone numbers: ")
        phones = input_phones.split()

    else:
        with open(args.input_file_path, 'r') as input_file:
            input_phones = input_file.readlines(99) # limiting request with first 99 lines in text-file to avoid flood wait error
        
        # remove spaces and newlines in the phones
        phones = [tlf.strip('\n').replace(' ','') for tlf in input_phones]

    result = user_validator(phones)
    print(result)

    # If we have an output filename, save the csv
    if args.output_filename:
        csv = "telephone,username\n"
        for phone, username in result.items():
            csv += f"{phone},{username}\n"

        with open(args.output_filename, 'w') as output_file:
            output_file.write(csv)
