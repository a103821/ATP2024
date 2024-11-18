

Raciocínio por trás do código:

1. Desenho da Casa

 O primeiro bloco de código desenha uma casa composta por um quadrado e um triângulo no topo, representando o telhado.

- Pen Up e movimentos: A tartaruga é movida para a posição adequada antes de começar a desenhar.
- Quadrado: A casa começa com quadrado usando `repeat 4 times` para mover para frente e virar, criando os lados.
- Telhado: Após desenhar o quadrado, há uma sequência de movimentos para formar o triângulo do telhado.

2. Desenho da árvore 
O bloco do meio gera uma árvore, composto por um semicírculo e um tronco retangular. O raciocínio principal é:

- Pen Up e movimentações: A tartaruga é inicialmente movida para a posição adequada antes de começar a desenhar.
- Parte superior:Um semicírculo para representar a copa da árvore.
- Parte inferior: Um retângulo simples desenhado através de um conjunto de instruções `move forward` e `turn`.

3. Desenho do Sol
O último bloco é responsável pelos círculo no topo da imagem.

- Movimentos Circulares: Aqui, a tartaruga desenha o círculo utilizando o bloco `repeat 360 times` com pequenos movimentos de frente e pequenas rotações. 

Estrutura do Código
- A estrutura repetitiva (loops) é usada para formar formas geométricas (quadrado, círculo).
- Movimentação controlada através de comandos de `turn` e `move forward` para posicionar a tartaruga corretamente para o próximo desenho.
- Uso de ângulos e tamanhos ajustados para desenhar as formas com precisão, especialmente no telhado da casa e na copa da arvore.
