#!/usr/bin/env python 

import hashlib
import hmac
import requests
import datetime
import random
import os
import time
import fire
import json

class BlinkTradeCli(object):
  def __init__(self, broker_id=11,
               verbose=False,
               show_header=True,
               blinktrade_api_key=None,
               blinktrade_api_secret=None):
    self._verbose = verbose
    self._show_header = show_header
    self._broker_id = broker_id
    self._key = blinktrade_api_key
    self._secret = blinktrade_api_secret
    if not blinktrade_api_key:
      self._key = os.getenv('BLINKTRADE_API_KEY')
      assert self._key, 'No BLINKTRADE_API_KEY'
      self._secret = os.getenv('BLINKTRADE_API_SECRET')
      assert self._secret, 'No BLINKTRADE_API_SECRET'


  def _underscore_to_blinktrade_message_case(self,value):
    def camelcase():
      while True:
        yield str.capitalize
    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))

  def send_message(self, msg):
    TIMEOUT_IN_SECONDS = 10
    BLINKTRADE_API_VERSION = "v1"

    dt = datetime.datetime.now()
    nonce = str(int((time.mktime( dt.timetuple() )  + dt.microsecond/1000000.0) * 1000000))
    signature = hmac.new( self._secret,  nonce, digestmod=hashlib.sha256).hexdigest()
    headers = {
      'user-agent': 'blinktrade_tools/0.1',
      'Content-Type': 'application/json',
      'APIKey': self._key,
      'Nonce': nonce,
      'Signature': signature
    }

    blinktrade_api_url = "https://api.blinktrade.com"
    if self._broker_id == 11:
      blinktrade_api_url = "https://bitcambio_api.blinktrade.com"

    url = '%s/tapi/%s/message' % (blinktrade_api_url, BLINKTRADE_API_VERSION)

    if self._verbose:
      print('SEND', msg)

    try:
      response = requests.post(url, json=msg, verify=True, headers=headers, timeout=TIMEOUT_IN_SECONDS)
      if response.status_code == 200:
        return response.json()
    except Exception,e:
      print(str(e))
      raise e

  def get_list(self, list_msg_type, list_name, params, page=0, num_pages=None):
    res = []
    still_have_records_to_read = True

    while still_have_records_to_read:
      if num_pages and page > num_pages:
        break

      requestId = random.randint(1, 100000)
      msg = {
        "MsgType": list_msg_type,
        "Page": page,
        "PageSize": 20
      }
      req_id_field = list_name + 'ReqID'
      msg[req_id_field] = requestId
      msg.update(params)

      api_response = self.send_message(msg)
      if api_response['Status'] != 200:
        if self._verbose:
          print (api_response)
        return res

      api_responses = api_response['Responses']
      for response in api_responses:
        if req_id_field in response and response[req_id_field] == requestId:
          array_record_list = response[list_name + 'Grp']
          if len(array_record_list) < msg['PageSize']:
            still_have_records_to_read = False
          else:
            page += 1

          for array_record in array_record_list:
            if self._verbose:
              print (array_record)

            record = dict(zip(response['Columns'], array_record))
            res.insert(0, record)
    return res

  def _printout_result(self, res_header, res_body):
    if self._show_header:
      print (json.dumps(res_header)[1:-1])
    for line in res_body:
      print json.dumps(line)[1:-1]

  def list_withdrawals(self,status_list=None, page=0, num_pages=None):
    if status_list is None:
      status_list = "[]"

    res = self._handle_withdraw_list(
      self.get_list('U26', 'WithdrawList', {'StatusList': status_list}, page, num_pages))
    self._printout_result(res[0], res[1])

  def list_deposits(self,status_list=None, page=0, num_pages=None):
    if status_list is None:
      status_list = "[]"
    res = self._handle_deposit_list(
      self.get_list('U30', 'DepositList', {'StatusList': status_list}, page, num_pages))
    self._printout_result(res[0], res[1])


  def _handle_deposit_list(self, deposit_list):
    records = []
    for rec in deposit_list:
      if self._verbose == 1:
        print(rec)

      name = ""
      if "UserVerificationData" in rec and rec["UserVerificationData"] is not None:
        for d in rec["UserVerificationData"]:
          if "name" in d:
            name = " ".join([d["name"]["first"], d["name"]["middle"], d["name"]["last"]])
            break

      phone_number = ""
      if "UserVerificationData" in rec and rec["UserVerificationData"] is not None:
        for d in rec["UserVerificationData"]:
          if "phone_number" in d:
            phone_number = d["phone_number"]
            break

      identification = ""
      if "UserVerificationData" in rec and rec["UserVerificationData"] is not None:
        for d in rec["UserVerificationData"]:
          if "identification" in d:
            identification = d["identification"].values()[0]
            break

      receipt = ""
      if "Data" in rec:
        if "DepositReceipt" in rec["Data"]:
          receipt = rec["Data"]["DepositReceipt"][0]


      input_address = None
      input_txid = None
      is_double_spent = None
      reference = None
      from_account_branch = None
      from_account_number = None

      if "Data" in rec:
        if "InputAddress" in rec["Data"]:
          input_address = rec["Data"]["InputAddress"]
        if "InputTransactionHash" in rec["Data"]:
          input_txid = rec["Data"]["InputTransactionHash"]
        if "IsDoubleSpent" in rec["Data"]:
          is_double_spent = rec["Data"]["IsDoubleSpent"]
        if "sender_account_no" in rec["Data"]:
          from_account_number = rec["Data"]["sender_account_no"]
        if "agencia" in rec["Data"]:
          from_account_branch = rec["Data"]["agencia"]
        if "Reference" in rec["Data"]:
          reference = rec["Data"]["Reference"]
        elif "ref" in rec["Data"]:
          reference = rec["Data"]["ref"]
        elif "documento" in rec["Data"]:
          reference = rec["Data"]["documento"]

      rec = [
        rec["DepositID"],
        rec["Created"][:10],
        rec["Created"][11:],
        rec["State"],
        int(rec["Status"]),
        rec["Username"],
        rec["Value"] / 1e8,
        rec["PaidValue"] / 1e8,
        rec["CreditProvided"] / 1e8,
        rec["ControlNumber"],
        input_address,
        input_txid,
        is_double_spent,
        reference,
        from_account_branch,
        from_account_number,
        name,
        identification,
        phone_number,
        rec["DepositMethodName"],
        receipt
      ]
      if self._verbose:
        print (rec)
      records.append(rec)

    return ['ID',
            'Date',
            'Hour',
            'Method',
            'State',
            'Status',
            'Username',
            'DeclaredValue',
            'PaidValue',
            'CreditProvided',
            'ControlNumber',
            'Wallet',
            'TXID',
            'IsDoubleSpent',
            'Reference',
            'AccountBranch',
            'AccountNumber',
            'Name',
            'Identification',
            'PhoneNumber',
            'Receipt'], records



  def _handle_withdraw_list(self,withdraw_list):
    records = []
    for rec in withdraw_list:

      account_number = None
      if "AccountNumber" in rec["Data"]:
        account_number = rec["Data"]["AccountNumber"]

      account_holder_id = None
      if "CPFCNPJ" in rec["Data"]:
        account_holder_id = rec["Data"]["CPFCNPJ"]
      elif "CPF_CNPJ" in rec["Data"]:
        account_holder_id = rec["Data"]["CPF_CNPJ"]
      elif "VenezuelanID" in rec["Data"]:
        account_holder_id = rec["Data"]["VenezuelanID"]
      elif "ClientIDNr" in rec["Data"]:
        account_holder_id = rec["Data"]["ClientIDNr"]
        if "Issue Date ID" in rec["Data"]:
          account_holder_id += " Issued:" + rec["Data"]["Issue Date ID"]
        if "Place of Issue" in rec["Data"]:
          account_holder_id += " City:" + rec["Data"]["Place of Issue"]

      account_type = None
      if 'AccountType' in rec['Data']:
        account_type = rec['Data']['AccountType']
      elif 'Type' in rec['Data']:
        account_type = rec['Data']['Type']

      account_branch = None
      if "AccountBranch" in rec["Data"]:
        account_branch = rec["Data"]["AccountBranch"]
      elif "VPbankbranch" in rec["Data"]:
        account_branch = rec["Data"]["VPbankbranch"]
      elif "BankBranch" in rec["Data"]:
        account_branch = rec["Data"]["BankBranch"]
      elif 'Vietcombankbranch' in rec["Data"]:
        account_branch = rec["Data"]["Vietcombankbranch"]

      account_name = None
      if "AccountName" in rec["Data"]:
        account_name = rec["Data"]["AccountName"]
      elif "Clientname" in rec["Data"]:
        account_name = rec["Data"]["Clientname"]

      bank_number = None
      if 'BankNumber' in rec['Data']:
        bank_number = rec['Data']['BankNumber']

      bank_city = None
      if 'BankCity' in rec['Data']:
        bank_city = rec['Data']['BankCity']

      recipient_phone_number = None
      if "Phone Number of Recipient" in rec["Data"]:
        recipient_phone_number = rec["Data"]["Phone Number of Recipient"]
      elif "AccountHolderPhone" in rec["Data"]:
        recipient_phone_number = rec["Data"]["AccountHolderPhone"]

      transaction_id = None
      if 'TransactionID' in rec['Data']:
        transaction_id = rec['Data']['TransactionID']

      wallet = None
      if 'Wallet' in rec['Data']:
        wallet = rec['Data']['Wallet']

      rec = [
        rec["WithdrawID"],
        rec["Created"][:10],
        rec["Created"][11:],
        rec["Method"],
        rec["Username"],
        bank_number,
        bank_city,
        recipient_phone_number,
        account_branch,
        account_name,
        account_type,
        account_number,
        account_holder_id,
        wallet,
        transaction_id,
        rec["PaidAmount"] / 1e8,
        rec["Amount"] / 1e8,
        (rec["PaidAmount"] - rec["Amount"]) / 1e8,
        rec["PercentFee"],
        rec["Status"]
      ]
      if self._verbose:
        print (rec)
      records.append(rec)

    headers = ['ID', 'Date', 'Hour', 'Method', 'Username', 'BankNumber', 'BankCity', 'RecipientPhoneNumber',
               'AccountBranch', 'AccountName', 'AccountType', 'AccountNumber', 'AccountHolderID',
               'PaidAmount', 'Amount', 'PaidFees', 'Wallet', 'TransactionID',
               'PercentFee', 'Status']
    return headers, records


if __name__ == '__main__':
  fire.Fire(BlinkTradeCli)

