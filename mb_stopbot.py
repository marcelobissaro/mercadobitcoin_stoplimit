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
import tapi_methods
import sys
import argparse
import time
from argparse import RawTextHelpFormatter
import subprocess
import time
from time import localtime, strftime

parser = argparse.ArgumentParser(description="""

   *******************************************************************
   ***** ATENCAO! LEIA ESTE TUTORIAL ATENTAMENTE ANTES DE USAR *******
   *****    EU NAO ME RESPONSABILIZO SE VOCE TIVER PREJUIZO    *******
   *******************************************************************

 Esse bot funciona basicamente da seguinte maneira:

 1 - A cada X segundos, o bot verifica as ordens de compra do livro de ofertas

 2 - Quando ela atingir um valor menor que o estipulado por voce, significa que 
     muitas vendas aconteceram, e o preco caiu para um valor abaixo do que voce
     estipulou.

 3 - Nesse mesmo instante, o bot ira criar uma ordem de venda pelo valor que voce
     estipular, com a quantidade de moedas que voce definir.
     Essa ordem de venda podera ser de 2 tipos diferentes:

     3.1 - Ordem passiva
           Nessa caso, a ordem sera criada exatamente pelo valor que voce definir.
           O que significa que ela ficara em aberto no livro de ofertas, aguardando
           que alguem compre. Nesse modo de operacao, voce pagara menos taxa sobre a 
           venda (0.3%). Porem, corre o risco de a ordem nunca ser executada, caso o preco
           da moeda esteja em queda livre!

           Por exemplo:
             Ordem de compra no momento que voce inicia o script: 30.000
             Valor que voce estipula como sendo seu stop: 27.000
             Ordem de venda que voce gostaria que fosse criada nesse momento: 27.001

             Se a primeira ordem de compra do livro atingir 26.999, o bot ira criar
             uma ordem de venda no valor de 27.001. Porem, se o movimento de queda estiver
             acentuado, a moeda pode cair pra 26.000 e varias pessoas colocarao ordens de venda
             menor que a sua de 27.001 fazendo com que ela demore para ser executada. Ou talvez
             ela nem seja executada!

    3.2 - Ordem ativa
          Nesse caso, o bot ira criar uma ordem de venda pelo mesmo valor da primeira ordem de
          compra disponivel, fazendo assim com que a ordem seja executada imediatamente. 
          Esse tipo de ordem tem taxa maior, cobrada pela corretora: 0.7%.
          Esteja ciente que em caso de quedas fortes, voce podera vender por um valor abaixo do
          que gostaria.
          
          Por exemplo:
             Ordem de compra no momento que voce inicia o script: 30.000
             Valor que voce estipula como sendo seu stop: 27.000
             Em uma queda normal, quando a cotacao atingir 26.999 o STOP eh acionado, e uma ordem
             de venda eh criada no valor de 26.999 e portanto, executada imediamente

             Porem, caso a queda seja repentina, a cotacao pode cair de 27.001 (ainda nao ativou seu
             stop) para 26.000 em apenas 1 segundo, ativando portanto seu stop e fazendo com que o bot 
             crie a ordem de venda ativa pelo valor de 26.000.
              
             Isso eh muito comum de acontecer no MercadoBitcoin, devido a baixa volatilidade do mercado
             brasileiro! Uma venda de 200.000 reais por exemplo iria consumir dezenas de ordens do livro,
             fazendo o preco despencar algumas centenas de reais imediatamente! 

  Exemplos de uso:

  1 - Stop de 27000.00001 com limite de 27100 vendendo 0.1 Bitcoins

       > python mb_stopbot.py --moeda BTC --stop 27000.00001 --limite 27100 --quantidade 0.1
         Ou simplesmente:
       > python mb_stopbot.py -m BTC -s 27000.00001 -l 27100 -q 0.1

       Nesse caso, quando a primeira ordem de compra atingir um valor igual ou menor que
       27000.00001, uma ordem de venda sera criada no valor de 27100.

  2 - Stop de 650, para LTC, e do tipo que cria ordem ativa (portanto, nao precisa definir 
      o valor do limite) num total de 3 Litecoins

      > python mb_stopbot.py --moeda LTC --stop 650 --quantidade 3 --ativa
        Ou simplesmente:
      > python mb_stopbot.py -m LTC -s 650 -q 3 -a

      Nesse caso, quando a primeira ordem de compra atingir um valor igual ou menor que 
      650, uma ordem de venda sera criada pelo valor necessario para que os 3 Litecoins
      seja vendido instantaneamente. O bot ira percorrer todas os ordens de compra, somando
      suas quantidades, para que a ordem seja criada de maneira a ser consumida por inteiro
      instantaneamente.

  3 - Cancelando uma ordem de BitcoinCash que esta em andamento.
      O ID da ordem sera mostrado pra voce no output do bot, assim que for criada
      
      > python mb_stopbot.py --moeda BCH --cancel 1389438
        Ou simplesmente:
      > python mb_stopbot.py -m BCH -c 1389438

  
""", formatter_class=RawTextHelpFormatter)
parser.add_argument('-l', '--limite', help='Valor da ordem que sera criada, na quantidade estipulada pelo parametro -q', default=-1)
parser.add_argument('-s', '--stop', help='Quando atingir esse valor, crie a ordem de venda no valor estipulado pela opcao -q e -l', default=-1)
parser.add_argument('-m', '--moeda', help='Sigla da Moeda a ser usada. Pode ser BTC, LTC ou BCH', default=-1)
parser.add_argument('-q', '--quantidade', help='Quantidade da moeda que deseja vender', default=-1)
parser.add_argument('-c', '--cancel', help='ID da ordem que deseja cancelar', default=-1)
parser.add_argument('-a', '--ativa', help="""Define que a ordem devera ser executada no mesmo instante. 
Ou seja, cria uma ordem ativa.
""", nargs='?', const=True)

args = parser.parse_args()
limite = float(args.limite)
stop = float(args.stop)
quantidade = float(args.quantidade)
siglaMoeda = args.moeda
cancelar = int(args.cancel)
ativa = args.ativa

# A cada quantos segundos o bot deve checar pela cotacao
timeToSleep = 1

# De quanto em quanto tempo calcular o quao distante esta do stop
mostrarSituacaoAtualACada = 60 * 5 # 60 segundos vezes 5 = 5 minutos

# Variavel global pra armazenar as ordens lidas. As vezes uma leitura pode falhar,
# entao essa variavel sempre tera a ultima leitura.
global todasOrdens


# Validar se os parametros de entrada necessarios foram passados conforme esperado
def validarParametrosEntrada():
    if siglaMoeda != "BTC" and siglaMoeda != "LTC" and siglaMoeda != "BCH":
        myprint("Apenas BTC, LTC ou BCH pode ser usado")
        sys.exit(-1)
    
    if cancelar != -1:
        tapi_methods.cancel_order(cancelar, siglaMoeda)
        myprint("Ordem %s cancelada" % cancelar)
        sys.exit(0)
    
    if (limite == -1 and not ativa) or quantidade == -1 or stop == -1:
        myprint("Voce deve especificar o limite (-l), o stop (-s)  e a quantidade (-q)") 
        sys.exit(-1)
    
    if ativa and (stop == -1 or quantidade == -1):
        myprint("Voce deve especificar tambem o valor de STOP e a quantidade que deseja vender")
        sys.exit(-1)
    
    if ativa and limite != -1:
        myprint("Se voce deseja que a ordem seja executada instantaneamente, nao deve definir um limite.")
        myprint("O bot vendera pelo valor da ultima ordem de compra do livro, portanto, sera uma ordem ativa")
        sys.exit(-1)


# Funcao para imprimir as mensagens na tela de maneira customizada,
# com um timestamp
def myprint(message):
   print '%s - %s' % (strftime("%Y-%m-%d %H:%M:%S", localtime()), message)

def getTodasOrdens(moeda):
    orders=""
    orders_json=""
    global todasOrdens
    try:
        orders = subprocess.Popen("curl -s https://www.mercadobitcoin.net/api/%s/orderbook/" % moeda, shell=True, stdout=subprocess.PIPE).stdout.read()
        orders_json = json.loads(orders)
        todasOrdens = orders_json
    except Exception as e:
        print "Exception: %s" % e
        orders_json = todasOrdens
    return orders_json


def getPrimeiraDeVendaECompra():
    primeiraDeVenda = 0
    primeiraDeCompra = 0

    # Algumas vezes o sistema do MB falha, e retorna ordens com valor
    # zerado. Isso estava fazendo o bot achar que o preco tinha caido
    # a ativava o stop. Estou considerando que nunca uma ordem valera menos 
    # de 50 reais. Se Litecoin, Bitcoin ou BitcoinCash um dia cair pra baixo
    # disso, corra para as montanhas! :) 
    while primeiraDeVenda < 50 or primeiraDeCompra < 50:
        orderBook = getTodasOrdens(siglaMoeda)
        primeiraDeVenda = orderBook['asks'][0][0]
        primeiraDeCompra = orderBook['bids'][0][0]
    return [orderBook['asks'][0][0],orderBook['bids'][0][0]]

# Calcular qual o valor necessario que precisa ser usado
# pra criar a ordem de venda de maneira que ela seja consumida
# por inteiro, imediatamente. Por exemplo:
# Ordens de Compra no livro:
#  Valor    Quantidade
#  501         1
#  500.999     5
#  499         0.5
#  498         0.5
#
# Se voce deseja vendar 6.2 moedas, precisa que a ordem
# seja criada no valor de 499 para que seja consumida por inteiro
# Se voce deseja vendar 0.4 moedas, precisa que a ordem 
# seja criada no valor de 501 para que seja consumida por inteiro
# E assim por diante.
def getValorNecessarioParaConsumirTudo(quantidade):
    orderBook = getTodasOrdens(siglaMoeda)
    total = 0
    retornar = 0
    for ordem in orderBook['bids']:
        total += ordem[1]
        if total > quantidade:
            retornar = ordem[0]
            break
    return retornar

def colocarPraVender(totalPraVender, limite, ativa):
    primeiraDeVenda, primeiraDeCompra = getPrimeiraDeVendaECompra()
    myprint("Primeira ordem de venda do book : %s" % primeiraDeVenda)
    if not ativa: # Tipo de ordem que fica no book, aguardando execucao
       venderPor = limite
       myprint("Criando ordem de venda no valor : %s" % venderPor)
    else: # Ordem para executar imediatamente
       venderPor = getValorNecessarioParaConsumirTudo(totalPraVender)
       myprint("Vendendo instantaneamente pelo valor necessario para consumir os %.5f %s: %.5f" % (totalPraVender, siglaMoeda, venderPor))
 
    idOrdemVenda = placeOrdemVenda(totalPraVender, float(("%.5f" % (int(venderPor * 100000) / float(100000)))))
    myprint("")
    time.sleep(5) # Aguardando alguns segundos pra dar tempo da ordem executar, e isso refletir na API

    # Entrando em um loop ate que toda a quantidade seja vendida
    # Se a mercado estiver muito ativo as ordens do livro podem variar
    # mais rapido do que esse script levou pra calcular as coisas, e talvez
    # ficar resquicios de venda pra tras.
    while True:
        if ativa: # Ordens que executam instantaneamente
            if not ordemDeFatoFinalizada(idOrdemVenda):
                # Ordem que deveria ter sido executada por inteiro pelo visto ainda nao foi, por algum motivo
                # Entao cancele-a e coloque de novo
                myprint(" WARNING: Ordem que deveria ter sido executada por completo ainda nao foi")
                cancelamento = cancelandoOrdemERetornandoDetalhesOperacao(idOrdemVenda)
                pendente = float(cancelamento['quantity']) - float(cancelamento['executed_quantity'])
                myprint(" Quantidade ainda pendente: %s" % pendente)
                if pendente > 0: # Ainda tem alguma coisa pendente pra ser vendido
                    colocarPraVender(pendente, limite, ativa) 
                else: # Situacao super inesperada. Eu estou tratando uma situacao onde a ordem nao finalizou
                      # mas ainda assim a quantiadde pendente esta como zero! Isso pode significar que tudo foi de fato
                      # vendido, entao por seguranca marca como vendido
                    myprint(" ****** Vendido!!! ****** Venda feita por R$%s" % venderPor)
                    break

            else: # Ordem finalizada como esperado
                 myprint(" ****** Vendido!!! ****** Venda feita por R$%s" % venderPor)
                 break
        else: 
            myprint("Ordem pendente no livro, aguardando execucao")
            break


# Cancelar a ordem, e retornar os detalhes da operacao que a API fornece
def cancelandoOrdemERetornandoDetalhesOperacao(id_ordem):
    response = tapi_methods.cancel_order(id_ordem, siglaMoeda)
    myprint(" Ordem cancelada : %s" % (id_ordem))
    return response['response_data']['order']

# Verificando se o status da ordem eh de fato de ordem finalizada.
def ordemDeFatoFinalizada(idOrdem):
    response_json = tapi_methods.get_order(idOrdem, siglaMoeda)
    # 2 : open : Ordem aberta, disponivel no livro de negociacoes. Estado intermediario.
    # 3 : canceled : Ordem cancelada, executada parcialmente ou sem execucoes. Estado final.
    # 4 : filled : Ordem concluida, executada em sua totalidade. Estado final.
    if response_json['response_data']['order']['status'] != 2:
        return True
    else:
        return False

# Criar a ordem de venda
def placeOrdemVenda(totalPraVender, venderPorQuanto):
    response_json = tapi_methods.place_sell_order(totalPraVender, venderPorQuanto, siglaMoeda)
    order_id = 0
    try:
        order_id = response_json['response_data']['order']['order_id']
    except:
        myprint("*********** ERRO CATASTROFICO: NAO FOI POSSIVEL CRIAR A ORDEM DE VENDA. ABORTANDO EXECUCAO *********** ")
        myprint("Debug information: %s" % response_json)
        sys.exit(-1)
        
    myprint("ID da ordem de venda criada : %s (%s %s por R$%s)" % (order_id, totalPraVender, siglaMoeda, venderPorQuanto))
    return order_id

# Imprimir detalhes das ordens abertas encontradas
def printDetalhesOrdens(moeda):
   # Tipo de ordem igual a 2 significa ordens abertas
   ordens = tapi_methods.list_orders('2', moeda)
   for ordem in ordens['response_data']['orders']:
      if ordem['order_type'] == 1:
         ordertype="Compra"
      else:
         ordertype="Venda"
      myprint("            Tipo      : Ordem de %s" % ordertype)
      myprint("            Ordem ID  : %s" % ordem['order_id'])
      myprint("            Valor     : R$%.6f" % float(ordem['limit_price']))
      myprint("            Quantidade: %.6f" % float(ordem['quantity']))
      myprint("")


# Leia os dados da conta do usario, e as inforamcoes das ordens
# abertas.
def printResumoFinanceiro():
    acc_info = tapi_methods.getAccountInfo(siglaMoeda)
    myprint("INICIANDO SCRIPT")
    myprint("OPERANDO MOEDA          : %s" % (siglaMoeda))
    myprint("STOP ESTIPULADO         : %s" % stop)
    mostrarLimite = "Valor da primeira ordem de compra que estiver no book no momento" if ativa else limite 
    myprint("VALOR DA ORDEM (LIMITE) : %s" % mostrarLimite)
    myprint("QUANTIDADE A SER USADA  : %.6f %s" % (quantidade, siglaMoeda))
    myprint("")
    myprint("Saldo em Reais:")
    myprint("   Disponivel pra usar        : R$%.2f" % float(acc_info['response_data']['balance']['brl']['available']))  
    myprint("   Pendente em ordens abertas : R$%.2f" % (float(acc_info['response_data']['balance']['brl']['total']) - float(acc_info['response_data']['balance']['brl']['available'])))
    myprint("")
    myprint("Saldo de BTC:")
    myprint("   Disponivel pra usar        : %.7f" % float(acc_info['response_data']['balance']['btc']['available']))
    myprint("   Pendente em ordens abertas : %.7f" % (float(acc_info['response_data']['balance']['btc']['total']) - float(acc_info['response_data']['balance']['btc']['available'])))
    myprint("   Total de ordens abertas    : %s" % acc_info['response_data']['balance']['btc']['amount_open_orders'])
    if acc_info['response_data']['balance']['btc']['amount_open_orders'] > 0:
        printDetalhesOrdens('BTC')
    myprint("")
    myprint("Saldo de LTC:")
    myprint("   Disponivel pra usar        : %.7f" % float(acc_info['response_data']['balance']['ltc']['available']))
    myprint("   Pendente em ordens abertas : %.7f" % (float(acc_info['response_data']['balance']['ltc']['total']) - float(acc_info['response_data']['balance']['ltc']['available'])))
    myprint("   Total de ordens abertas    : %s" % acc_info['response_data']['balance']['ltc']['amount_open_orders'])
    if acc_info['response_data']['balance']['ltc']['amount_open_orders'] > 0:
        printDetalhesOrdens('LTC')
    myprint("")
    myprint("Saldo de BCH:")
    myprint("   Disponivel pra usar        : %.7f" % float(acc_info['response_data']['balance']['bch']['available']))
    myprint("   Pendente em ordens abertas : %.7f" % (float(acc_info['response_data']['balance']['bch']['total']) - float(acc_info['response_data']['balance']['bch']['available'])))
    myprint("   Total de ordens abertas    : %s" % acc_info['response_data']['balance']['bch']['amount_open_orders'])
    if acc_info['response_data']['balance']['bch']['amount_open_orders'] > 0:
        printDetalhesOrdens('BCH')
    myprint("")
    myprint("")
    stopAtingido = False

    # Verificando se tem a quantidade passada como parametro, ou se a quantidade passada
    # nao eh menor que o limite que a exchange aceita.
    primeiraDeVenda = 0
    primeiraDeCompra = 0
    if float(acc_info['response_data']['balance']['%s'%siglaMoeda.lower()]['available']) < quantidade:
       myprint("Voce nao tem %.6f %s disponivel pra usar. Abortando bot" % (quantidade,siglaMoeda))
       sys.exit(-1)
    if siglaMoeda == "BTC" or siglaMoeda == "BCH":
       if quantidade < 0.001:
          myprint("Limite minimo estipulado pela exchange eh de 0.001 BTC ou BCH. Abortando")  
          sys.exit(-1)
    else:
       if quantidade < 0.009:
          myprint("Limite minimo estipulado pela exchange eh de 0.009 LTC. Abortando")
          sys.exit(-1)


# Enderecos das minhas wallets para receber doacoes
def printInformacoesPraDoacoes():
    myprint("")
    myprint("Esse script lhe ajudou de alguma maneira? O que acha de fazer uma doacao? :) ")
    myprint("Carteira Bitcoin:     1DhnR664GMj68KNN71Ny3mtYQowoZH5fwv ")
    myprint("Carteira Liteoin:     LUzqATh2dMkvHLNSqL1GiuNNruv71ZCVaW ")
    myprint("Carteira BitcoinCash: bitcoincash:qpq289n5agnu2zk4q3mqfghrnqvlmuz28sh897sk48 ")

###################################################
############### INICIO DO SCRIPT ##################
###################################################
validarParametrosEntrada()
printResumoFinanceiro()

myprint("       MONITORAMENTO DAS ORDENS INICIADO") 
count = 0
while True:
   primeiraDeVenda, primeiraDeCompra = getPrimeiraDeVendaECompra()
   if primeiraDeCompra <= stop:
       myprint("")
       myprint("   ********************************************************************************")
       myprint("   *********** ORDEM DE COMPRA MENOR QUE O STOP FOI ATINGIDA: %s ***********  " % primeiraDeCompra)
       myprint("   ********************************************************************************")
       myprint("")
       stopAtingido = True
       break
   if count > mostrarSituacaoAtualACada or count == 0:
       myprint("Ordens de compra/venda no momento: %s -- %s" % (primeiraDeCompra, primeiraDeVenda))
       myprint("Se a ordem de compra baixar mais %s atinge o STOP" % (primeiraDeCompra - stop))
       myprint("")
       count = 0
   count += timeToSleep
   time.sleep(timeToSleep)

if stopAtingido:
    colocarPraVender(quantidade, limite, ativa)
    printInformacoesPraDoacoes()
