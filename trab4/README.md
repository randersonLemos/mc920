# Aplicando transformações geométricas e projetivas (trabalho 4)
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

Pronto, seu ambiente de trabalho que se chama **mc920-trab4** está configurado e carregado.

# Rodando o programa main.py para projeção geometrica de escala

```
python3 main.py -imagem_entrada assets/baboon.png -e 1.25 -m lagrange
python3 main.py -imagem_entrada assets/baboon.png -e 1.25 -m bicubic
python3 main.py -imagem_entrada assets/baboon.png -e 1.25 -m bilinear
python3 main.py -imagem_entrada assets/baboon.png -e 1.25 -m nearneighbours
```


# Rodando o programa main.py para projeção geometrica de rotação

```
python3 main.py -imagem_entrada assets/baboon.png -a 1.25 -m lagrange
python3 main.py -imagem_entrada assets/baboon.png -a 1.25 -m bicubic
python3 main.py -imagem_entrada assets/baboon.png -a 1.25 -m bilinear
python3 main.py -imagem_entrada assets/baboon.png -a 1.25 -m nearneighbours
```

# Rodando o programa main.py para projeção geometrica de escala pela definição de largura e altura

```
python3 main.py -imagem_entrada assets/baboon.png -d 300x400 -m lagrange
python3 main.py -imagem_entrada assets/baboon.png -d 300x400 -m bicubic
python3 main.py -imagem_entrada assets/baboon.png -d 300x400 -m bilinear
python3 main.py -imagem_entrada assets/baboon.png -d 300x400 -m nearneighbours
```
