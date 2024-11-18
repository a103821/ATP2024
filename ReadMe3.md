
Descrição Geral
Este código implementa um jogo chamado "Jogo dos Fósforos". O objetivo do jogo é evitar ser o jogador que retira o último fósforo. Existem dois modos de jogo: Modo Normal e Modo Computador. O jogador pode escolher jogar contra o computador em ambos os modos.

Detalhamento
Função Show:

Imprime o menu do jogo com as opções disponíveis: NORMAL, COMPUTADOR, e SAIR.
Função out:

Imprime uma mensagem de despedida e encerra o jogo.
Função normal:

Representa o modo normal do jogo.
Inicializa o jogo com 21 fósforos.
Alterna entre o jogador e o computador para retirar fósforos até que não reste nenhum.
O jogador pode retirar entre 1 e 4 fósforos em cada turno.
Se o jogador tentar retirar um número inválido de fósforos ou mais fósforos do que os disponíveis, é solicitado a tentar novamente.
O computador sempre tenta fazer com que a soma dos fósforos retirados pelo jogador e pelo computador em um turno seja igual a 5, se possível.
O jogo termina quando todos os fósforos são retirados. Se o jogador retira o último fósforo, ele perde; se o computador retira o último fósforo, o jogador ganha.
Função computador:

Representa o modo computador do jogo.
Inicializa o jogo com 21 fósforos.
O computador começa retirando entre 1 e 4 fósforos aleatoriamente.
O jogador é solicitado a retirar entre 1 e 4 fósforos em cada turno.
Se o jogador tentar retirar um número inválido de fósforos ou mais fósforos do que os disponíveis, é solicitado a tentar novamente.
O jogo termina quando todos os fósforos são retirados. Se o computador retira o último fósforo, o jogador perde; se o jogador retira o último fósforo, o jogo acaba.
Função menu:

Exibe o menu do jogo e solicita ao jogador que escolha uma opção.
O jogador pode escolher entre jogar no modo normal, jogar no modo computador, ou sair do jogo.
Dependendo da escolha do jogador, a função correspondente (normal ou computador) é chamada.
Se o jogador escolhe sair, a função out é chamada e o jogo termina.
Se o jogador insere uma opção inválida, uma mensagem de erro é exibida e o menu é encerrado.