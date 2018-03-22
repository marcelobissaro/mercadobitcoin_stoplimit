"""
StopLimitBot MercadoBitcoin
Copyright (C) 2018 Marcelo Bissaro

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import urllib
import json
import time
from time import localtime, strftime
import hashlib
import hmac
import httplib
import time
from collections import OrderedDict
import sys

# Valor do campo 'Identificador'
MB_TAPI_ID = 'ffffffffffffffff1111111111111111'

# Valor do campo 'Segredo'
MB_TAPI_SECRET = 'ebcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890'

REQUEST_HOST = 'www.mercadobitcoin.net'
REQUEST_PATH = '/tapi/v3/'
def myprint(message):
   print '%s - %s' % (strftime("%Y-%m-%d %H:%M:%S", localtime()), message)

# Funcao que ira submeter o request para a api. 
def execute_post_call(params):
   params = urllib.urlencode(params)
   params_string = REQUEST_PATH + '?' + params
   H = hmac.new(MB_TAPI_SECRET, digestmod=hashlib.sha512)
   H.update(params_string)
   tapi_mac = H.hexdigest()
   # Gerar cabecalho da requisicao
   headers = {
       'Content-type': 'application/x-www-form-urlencoded',
       'TAPI-ID': MB_TAPI_ID,
       'TAPI-MAC': tapi_mac
   }
   # Realizar requisicao POST
   try:
       conn = httplib.HTTPSConnection(REQUEST_HOST)
       conn.request("POST", REQUEST_PATH, params, headers)
       response = conn.getresponse()
       response = response.read()

       # Eh fundamental utilizar a classe OrderedDict para preservar a ordem dos elementos
       response_json = json.loads(response, object_pairs_hook=OrderedDict)
   finally:
       if conn:
           conn.close()
   return response_json

def list_orders(ordertype, moeda):
   response=""
   while True:
      try:
         tapi_nonce = str(int(time.time()*1000))
         params = {
             'tapi_method': 'list_orders',
             'tapi_nonce': tapi_nonce,
             'coin_pair': 'BRL%s' % moeda,
             'status_list': '[%s]' % ordertype
         }
         response = execute_post_call(params)
         if 'status_code' in response:
            if response['status_code'] == 203:
               # TAPI_NONCE menor que o ultimo utilizado. Espera 5 segundos e tente de novo
               time.sleep(5)
               continue
            elif response['status_code'] != 100:
               raise Exception('Falhou alguma coisa %s' % response)
         if 'response_data' not in response:
            raise Exception('Sem resposta para listar ordens %s' % response)
      except Exception as e:
         myprint("*** Exception pra listar ordens %s ****" % e)
         time.sleep(1)
      else:
         break
   return response

def get_account_info(siglaMoeda):
   response=""
   while True:
      try:
         tapi_nonce = str(int(time.time()*1000))
         params = {
             'tapi_method': 'get_account_info',
             'tapi_nonce': tapi_nonce,
             'coin_pair': 'BRL%s' % siglaMoeda
         }
         response = execute_post_call(params)
         if 'status_code' in response:
            if response['status_code'] == 203:
               # TAPI_NONCE menor que o ultimo utilizado. Espera 5 segundos e tente de novo
               time.sleep(5)
               continue
            elif response['status_code'] == 201 or response['status_code'] == 202: 
               raise Exception('Valor da chave de autenticacao (TAPI-ID ou TAPI-SECRET) eh invalido')
            elif response['status_code'] != 100:
               raise Exception('Falhou alguma coisa %s' % response)
         if 'response_data' not in response:
            raise Exception('Sem resposta para colocar ordem de venda %s' % response)
      except Exception as e:
         myprint("*** Exception pra ler dados da conta:  %s ****" % e)
         time.sleep(1)
         sys.exit(-1)
      else:
         break
   return response


def place_sell_order(quantity, limit_price, siglaMoeda):
   response=""
   while True:
      try:
         tapi_nonce = str(int(time.time()*1000))
         params = {
             'tapi_method': 'place_sell_order',
             'tapi_nonce': tapi_nonce,
             'coin_pair': 'BRL%s' % siglaMoeda,
             'quantity': '%s' % quantity,
             'limit_price': '%s' % limit_price
         }
         response = execute_post_call(params)
         if 'status_code' in response:
            if response['status_code'] == 203:
               # TAPI_NONCE menor que o ultimo utilizado. Espera 5 segundos e tente de novo
               time.sleep(5)
               continue
            elif response['status_code'] == 232:
               raise Exception("Quantidade de moedas insuficiente.")
            elif response['status_code'] == 222 or response['status_code'] == 223 or response['status_code'] == 234:
               raise Exception("Quantidade de moedas para vender eh muito baixa (Limite eh de 0.001 para BTC e BCH, e 0.009 pra LTC")
            elif response['status_code'] != 100:
               raise Exception('Falha desconhecida: %s' % response)
         if 'response_data' not in response:
            raise Exception('Sem resposta para colocar ordem de venda %s' % response)
      except Exception as e:
         myprint("*** Exception pra criar ordem de venda: %s ****" % e)
         time.sleep(1)
         sys.exit(-1)
         break
      else:
         break
   return response

def getAccountInfo(moeda):
   response_json = get_account_info(moeda)
   saldo = 0
   if response_json['status_code'] != 100:
       myprint("Erro lendo dados da conta")
       print json.dumps(response_json, indent=4)
   return response_json

def cancel_order(order_id,siglaMoeda):
   response=""
   while True:
      try:
         tapi_nonce = str(int(time.time()*1000))
         params = {
             'tapi_method': 'cancel_order',
             'tapi_nonce': tapi_nonce,
             'coin_pair': 'BRL%s' % siglaMoeda,
             'order_id': order_id
         }
         response = execute_post_call(params)
         if 'status_code' in response:
            if response['status_code'] == 203:
               # TAPI_NONCE menor que o ultimo utilizado. Espera 5 segundos e tente de novo
               time.sleep(5)
               continue
            elif response['status_code'] == 212:
               # Ordem ja finalizada
               # Sleep de 2 segundos so pra evitar o estouro de acesso
               # a API
               time.sleep(2)
               response = get_order(order_id,siglaMoeda)
               raise Exception('Ordem ja finalizada. Lida novamente: %s' % response)
            elif response['status_code'] != 100:
               raise Exception('Falhou alguma coisa %s' % response)
         if 'response_data' not in response:
            raise Exception('Sem resposta para cancelar ordem de venda: %s' % response)
      except Exception as e:
         myprint("*** Exception pra cancelar ordem: %s ****" % e)
         time.sleep(2)
         if ordemJaEstaCanceladaOuVendida(order_id,siglaMoeda):
            break
      else:
         break
   return response

def get_order(order_id,siglaMoeda):
   while True:
      try:
         tapi_nonce = str(int(time.time()*1000))
         params = {
             'tapi_method': 'get_order',
             'tapi_nonce': tapi_nonce,
             'coin_pair': 'BRL%s' % siglaMoeda,
             'order_id': order_id
         }
         response = execute_post_call(params)
         if 'status_code' in response:
            if response['status_code'] == 203:
               # TAPI_NONCE menor que o ultimo utilizado. Espera 5 segundos e tente de novo
               time.sleep(5)
               continue
            elif response['status_code'] != 100:
               raise Exception('Falhou alguma coisa %s' % response)
         if 'response_data' not in response:
            raise Exception("Sem resposta para pegar detalhes da ordem: %s" % response)
      except Exception as e:
         myprint("*** Exception pra pegar detalhes da ordem: %s ****" % e)
         time.sleep(1)
      else:
         break
   return response

