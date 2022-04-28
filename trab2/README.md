# Escondendo uma mensagem em uma imagem (trabalho 1)
Documento sintético para auxiliar o usuário na execução dos códigos do projeto. Para informações mais detalhadas consultar o arquivo REPORT.pdf.

# Configurando ambiente de trabalho
O ambiente de trabalho desse projeto pode ser facilmente configurado com o auxílio do gerenciador de pacotes e ambientes Conda. Este documento assume que o usuário tenha tal gerenciador instalado.

Para configurar o ambiente executar:

> conda env create -f environment.yml

Depois de configurar o ambiente de trabalho é necessário carregá-lo. Para isso basta executar:

> source source.sh

Pronto, seu ambiente de trabalho que se chama **mc920-trab2** está configurado e carregado.

# Rodando os programas codificar.py, decodificar.py e mostrar_planos.py

> python3 codificar.py -imagem_entrada=png/watch.png -texto_entrada=txt/texto1.txt -planos_bits=0

> python3 decodificar.py -imagem_entrada=out/watchm_plano0_texto1.png -plano_bits=0

> python3 mostrar_planos.py -imagem_entrada=out/watchm_plano0_texto1.png -planos_bits=0:1:2:7
