python codificar.py -imagem_entrada=png/watch.png -texto_entrada=txt/texto1.txt -plano_bits=0

python decodificar.py -imagem_entrada=out/watchm_plano0.png -plano_bits=0

python mostrar_planos.py -imagem_entrada=out/watchm_plano0.png -plano_bits=0:1:2:7


python mostrar_planos.py -imagem_entrada=out/baboonm_plano0.png -plano_bits=0:1:2:7
