import json
import requests
import yaml
import boto3

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Parameters:
    def __init__(self, file_path='parameters.yml'):
        self.file_path = file_path
        self.if_file_exist = True

        try:
            fl = open(file=self.file_path, mode='r').read()
            params = yaml.load(fl, Loader)

            self.__URL_TICKER = params['URL_TICKER']
            self.__LIST_OF_PAIRS = params['LIST_OF_PAIRS']

        except FileNotFoundError as e:
            self.if_file_exist = False
            raise e

    def get_url_ticker(self):
        return self.__URL_TICKER

    def get_list_of_pairs(self):
        return self.__LIST_OF_PAIRS


def lambda_handler(event, context):

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('TradePrice')

    parameters = Parameters()
    if not parameters.if_file_exist:
        return None

    for pair in parameters.get_list_of_pairs():
        url = parameters.get_url_ticker() + pair
        try:
            response = requests.get(url)
            context = response.text
            if len(context) > 0:
                json_data = json.loads(context)

                if json_data['status']:

                    data_to_insert = {}

                    data_to_insert['id'] = json_data[pair]['updated']

                    for key, value in json_data[pair].items():
                        data_to_insert[key] = value

                    table.put_item(Item=data_to_insert)

        except requests.RequestException as e:
            print(e)
            raise e

        # print(json_data)
        # if json_data['status']:
        #     print(json_data[pair])

    return {
        "statusCode": 200,
        # "000": pr.URL_TICKER,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
