EFM = '!@#FIM#@!' # End of Message

factor = 1.5
row = 512
col = 512
cha = 3

total = int(factor*row*col*cha / 8)

texto = ''.join(['a']*total)

texto = texto[:-len(EFM)] + EFM

with open('texto_longo_2.txt', 'w') as fh:
    fh.write(texto)
