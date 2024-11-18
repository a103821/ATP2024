Descrição Geral:
Este código implementa um jogo de adivinhação de números com duas opções de jogo: o usuário adivinha o número que o computador pensou 
ou o computador adivinha o número que o usuário pensou.
 O código utiliza entradas do usuário para navegar entre os modos e para fazer suposições no jogo.

Detalhe:
Mensagem de Boas-vindas e Menu de Opções:

O programa imprime uma mensagem de boas-vindas detalhando as opções disponíveis:
Modo Computador: O jogador adivinha o número que o computador está pensando.
Modo Normal: O computador adivinha o número que o jogador está pensando.
Sair: Encerra o jogo.
Solicitação de Escolha do Usuário:

O programa solicita ao usuário que escolha uma das opções acima, inserindo um número correspondente (0 para sair, 1 para modo computador, 2 para modo normal).
Opção 0 - Sair:

Se o usuário escolher a opção 0, o programa imprime "Adeus!" e termina a execução.
Opção 1 - Modo Computador:

O computador gera um número aleatório entre 0 e 100.
O usuário é solicitado a adivinhar o número.
A cada palpite, o programa informa se o número adivinhado pelo usuário é maior, menor ou igual ao número pensado pelo computador.
O número de tentativas é contado e exibido quando o usuário adivinha corretamente.
Opção 2 - Modo Normal:

O jogador pensa em um número entre 0 e 100.
O computador faz suposições usando uma estratégia de busca binária.
O jogador deve responder se o número do computador é "acertou", "maior" ou "menor" em relação ao número que ele pensou.
O número de tentativas é contado e exibido quando o computador adivinha corretamente.
Se a resposta do usuário for inválida, o programa solicita uma nova resposta.

Interação com o Usuário
Modo Computador:

O computador escolhe um número.
O usuário tenta adivinhar.
O computador dá dicas ("menor" ou "maior").
O processo continua até o usuário acertar, e o número de tentativas é exibido.

Modo Normal:

O usuário pensa em um número.
O computador faz suposições.
O usuário responde se a suposição do computador é correta, maior ou menor.
O processo continua até o computador acertar, e o número de tentativas é exibido.