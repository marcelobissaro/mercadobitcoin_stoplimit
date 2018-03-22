# GOSTOU DO BOT? DOE QUALQUER QUANTIA PARA

> Carteira Bitcoin:     1DhnR664GMj68KNN71Ny3mtYQowoZH5fwv

> Carteira Liteoin:     LUzqATh2dMkvHLNSqL1GiuNNruv71ZCVaW

> Carteira BitcoinCash: bitcoincash:qpq289n5agnu2zk4q3mqfghrnqvlmuz28sh897sk48

# USE COM RESPONSABILIDADE

- É importante que voce leia todas as instruções desse tutorial, e entenda perfeitamente como o mercado funciona, como ordens de Stop-Limit funcionam, e como esse bot funciona.

***Eu não me responsabilizo se algo der errado, e voce vier a ter perdas com a utilização desse bot, mesmo que voce o faça da maneira correta!***

**Leia com atenção a seção 'O QUE PODE DAR ERRADO' desse documento, pra entender as limitações.**

# COMO ESSE BOT FUNCIONA

A intenção desse bot é monitorar as ordens de compra e venda na exchange brasileira 'MercadoBitcoin': https://www.mercadobitcoin.com.br e assim que a ordem de compra
ficar abaixo de determinado limite, o bot vende a quantidade de moedas que voce definir ao rodar o bot. A ordem de venda poderá ser do tipo 'Limite' (também conhecida como Passiva, ou Executada) ou do tipo 'Mercado' (também conhecida como Ativa, ou Executora)

O bot funciona para as 3 moedas que atualmente são negociadas nessa exchange: Bitcoin, Litecoin e BitcoinCash

O bot ainda não funciona para colocar ordens de compra se a cotação subir demais. Por enquanto, a proteção é para quando o preço cair abaixo de determinado valor.

# O QUE É NECESSÁRIO PARA EXECUTA-LO

1. Gerar uma chave de acesso no MercadoBitcoin (veja a seção seguinte)

2. Acesso à uma máquina Linux ou Mac. Não testei em Windows, então talvez voce precise instalar um Linux em uma máquina virutal no seu Windows primeiro. Veja mais informações aqui:
http://www.techtudo.com.br/dicas-e-tutoriais/noticia/2016/04/como-instalar-o-ubuntu-com-o-virtualbox.html

3. Python 2.7.10 ou superior instalado no seu Mac ou Linux. Geralmente ele vem nativo nesses sistemas. Caso não venha, pesquise no Google sobre como instalar.

4. Um conhecimento básico em utilização de linha de comando Linux é bem vindo.

# GERANDO SUA CHAVE DE ACESSO NO MERCADOBITCOIN

1. Acesse: https://www.mercadobitcoin.com.br/trade-api/configuracoes/

2. Escolha um nome pra chave, e clique em 'Criar Nova'

3. Acesse: https://www.mercadobitcoin.com.br/configuracoes/pin/  e peça para enviar um novo PIN. Voce o receberá por email.

4. Acesse https://www.mercadobitcoin.com.br/trade-api/configuracoes/ novamente e digite o PIN que recebeu no passo anterior e clique em OK.

5. Para o nome que voce escolheu no passo 2, mude o status para 'Acesso Total' clicando nas setinhas verdes.

6. Anote as 2 chaves, e coloque-as no arquivo 'tapi_methods.py' desse bot nas variáveis MB_TAPI_ID e MB_TAPI_SECRET no lugar indicado mas primeiras linhas do arquivo.

# RODANDO O BOT

1 - Para rodar o bot:

> python mb_stopbot.py <parametros>

# PARAMETROS DO BOT

Para ver detalhes de cada parametro, rode-o com -h
> python mb_stopbot.py -h

***É TOTALMENTE RECOMENDADO QUE VOCE RODE ASSIM A PRIMEIRA VEZ, E LEIA O TUTORIAL INTEIRO, COM CALMA!***

***SUGESTÃO: RODE AS PRIMEIRAS VEZES COM O VALOR MÍNIMO PERMITIDO PELA EXCHANGE, PRA EVITAR PROBLEMAS MAIORES: 0.001 para BTC e BCH, e 0.009 pra LTC***

-l: Valor limite da ordem que sera criada, na quantidade estipulada pelo parametro -q

-s: Quando atingir esse valor, crie a ordem de venda no valor estipulado pela opcao -q e -l

-m: Sigla da moeda a ser usada. Pode ser BTC, LTC ou BCH

-q: Quantidade da moeda que deseja vender

-c: ID da ordem que deseja cancelar

-a: Define que a ordem devera ser executada no mesmo instante.

# EXEMPLOS DE USO

> python mb_stopbot.py -m BTC -s 30000 -q 0.0023 -a

   Para Bitcoin, o bot irá esperar a primeira ordem de compra do livro de ofertas cair abaixo de R$30.000,00, e quando isso acontecer ele criará uma ordem de venda de 0.0023 pelo valor que for necessário para que a ordem seja executada imediatamente! Ou seja, se a primeira ordem de compra do livro for de R$29.500, a venda ocorrerá imediatamente por R$29.500, e pegando a taxa máxima, que no caso do MercadoBitcoin é de 0.7%


> python mb_stopbot.py -m LTC -s 600 -q 0.9345 -l 620

Para Litecoin, o bot irá esperar a primeira ordem de compra do livro de ofertas cair abaixo de 600, e quando isso acontecer ele criará uma ordem de venda de 0.9345 pelo valor de 620. Isso fará com que a ordem fique pendente no livro de ofertas, esperando para ser concretizada! Ou seja, se a primeira ordem de compra do livro for de 590, a ordem de venda será criada no valor de 620 e caso venha a se concretizar, pagará a taxa de ordem passiva que é de 0.3%

Cuidado com esse tipo de operação! Como o MercadoBitcoin tem baixo volume, é muito comum o preço despencar algumas dezenas de reais em menos de 5 segundos! Mesmo que voce coloque uma ordem abaixo do seu stop (Por exemplo, stop em 600 e limite em 590) essa ordem pode nao vir a ser executada, porque no momento que a ordem bateu 601 (portanto, ainda sem ativar o seu stop) ela caiu instantaneamente para 570. O bot iria cria a ordem por 590 mas não adiantaria, porque o preço ja estaria em 570.


> python mb_stopbot.py -m BCH -c 1245455

Cancela a ordem de BitcoinCash cujo ID é 1245455. Isso será util caso voce interrompa a execução do bot e alguma ordem esteja pendente. No começo da execução do bot voce verá todas as ordens que estão abertas na sua conta, e quando uma nova for criada voce também verá esse ID.

# O QUE PODE DAR ERRADO

Muitas coisas podem dar errado. Vou listar algumas:

1. Sua internet cair

   Lembre-se que o bot fica rodando o tempo todo, e precisa ler a cotação do site em tempo real! Sem saber a cotação atualizada, o bot não tem como agir e a sua ordem poderá não ser criada.

2. Sua energia cair

   Vide item anterior

3. Sua máquina desligar ou travar

   Vide item anterior

4. O site MercadoBitcoin parar de responder

   Vide item anterior

4. O MercadoBitcoin suspender a acesso às APIs

   Vide item anterior

5. O bot cair em algum situação que eu não previ

   Nesse caso, o bot irá lançar uma exceção e terminar sua execução.

6. A cotação despencar para um valor muito baixo, ativar sua ordem, e em seguida voltar o valor lá pra cima.

   Infelizmente isso é bastante possível de acontecer em uma exchange com baixo volume como as exchanges brasileiras. Esteja ciente disso ao planejar o valor da sua ordem.

7. Algum hacker acessar suas chaves de acesso e roubar todo seu dinheiro

   Com acesso as suas chaves de acesso, um hacker pode transferir suas moedas para outras carteiras, e não terá nada que voce possa fazer. O MercadoBitcoin não se responsabiliza por isso e muito menos eu :)

***LEMBRE-SE: EU NÃO ME RESPONSABILIZO POR NADA, SE ALGO DER ERRADO!! ESSE BOT É DE CÓDIGO ABERTO E VOCE É RESPONSÁVEL POR ENTENDER COMO ELE FUNCIONA E USA-LO DE MANEIRA SEGURA.***

# CONTATO

Qualquer dúvida, crítica ou sugestão, envie um email para mbissaro arroba gmail ponto com

