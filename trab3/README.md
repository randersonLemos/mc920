# Detectando transições abruptas em videos (trabalho 3)
Documento sintético para auxiliar o usuário na execução dos códigos do projeto. Para informações mais detalhadas consultar o arquivo REPORT.pdf.

# Configurando ambiente de trabalho
O ambiente de trabalho desse projeto pode ser facilmente configurado com o auxílio do gerenciador de pacotes e ambientes Conda. Este documento assume que o usuário tenha tal gerenciador instalado.

Para configurar o ambiente executar:

```
conda env create -f environment.yml
```

Depois de configurar o ambiente de trabalho é necessário carregá-lo. Para isso basta executar:

```
source source.sh
```

Pronto, seu ambiente de trabalho que se chama **mc920-trab3** está configurado e carregado.

# Rodando o programa main.py

```
python3 main.py -video_entrada=assets/lisa.mpg
```
