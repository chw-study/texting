import nexmo
from dotenv import load_dotenv
from os import getenv
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

def get_numbers(path, sheet, key, alt_key):
    df = pd.read_excel(path, dtype=str, sheet_name=sheet)
    nums = df[key].astype(str)
    alt_nums = df[alt_key].astype(str)
    together = [[x for x in i if x != 'nan'] for i in zip(nums, alt_nums)]
    return together

def get_result(num, r):
    try:
        message = r.get('messages', [])[0]
    except IndexError:
        message = {}

    return  {
        'num': num,
        'recorded_num': message.get('to'),
        'status': message.get('status'),
        'timestamp': datetime.utcnow()
    }


class Sender():
    def __init__(self, client, content):
        self.client = client
        self.content = content

    def send_message(self, numbers, idx = 0):
        sender = "NBI"

        for phone in numbers:
            print(phone)
            res = self.client.send_message({
                'from': sender,
                'to': str(phone),
                'text': self.content })

            result = get_result(phone, res)

            if result['status'] == '0':
                return result

        return result


def send_and_update(nums, content, results_file):
    client = nexmo.Client(key=getenv('NEXMO_KEY'), secret=getenv('NEXMO_SECRET'))
    s = Sender(client, content)
    with ThreadPoolExecutor(50) as pool:
        results = pool.map(s.send_message, nums)
    df = pd.DataFrame(results)
    df.to_csv(results_file, index=False)

def main(filename, sheet, column, alt_column, results_file, content):
    nums = get_numbers(filename, sheet, column, alt_column)
    send_and_update(nums, content, results_file)

from clize import run

if __name__ == '__main__':
    run(main)
