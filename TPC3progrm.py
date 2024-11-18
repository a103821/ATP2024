
import random

def Show():
    print('''JOGO DOS FÓSFOROS
            -------MENU--------
            -------------------
            ------NORMAL-------
            -------------------
            ----COMPUTADOR-----
            -------------------
            -------out--------''')

def out():
    print("Saiu do Jogo! Até à próxima!")

def normal():
        
    print("Está a jogar no Modo Normal")
    f = 21

    while f > 0:                
            while True:
                fj = int(input("Quanto fósforos queres tirar? (1, 2 ,3 ou 4)"))
                if  fj not in  [1, 2, 3, 4] or fj > f: #
                    print("Inválido. Tenta outro nº de fósforos.") 
                    break

                f = f - fj
                print(f"Tiraste {fj} fósforos. Faltam {f} fósforos!")
                    
                if f == 0:
                    print("Perdeste o jogo! Tiraste o último fósforo!")
                    break

                if f >= 5:
                    fcom = (5 - fj) 
                else: 
                    fcom = f - 1 
                
                f = f - fcom
                print(f"O computador tirou {fcom} fósforos. Restam {f} fósforos.")

                if f == 0:
                    print("Parabéns! O computador perdeu.")
                    break
                     
            
def computador():

    print("Estás a jogar no Modo Computador")
    f = 21

    while f > 0:

            fcom = random.randint(1,4)
            f = f - fcom
            print(f"O computador tirou {fcom} fósforos. Restam {f} fósforos!")

            if f == 0:
                print("O computador venceu! Tiraste o último fósforo.")
                break 


            while True:

                fj = int(input("Quantos fosfóros queres tirar? 1, 2, 3 ou 4?"))

                if fj not in [1, 2, 3, 4] or fj > f:
                    print("Inválido!Tente novamente!")
                    break

            f = f - fj
            print(f"Tiraste {fj} fósforos. Restam {f} fósforos!")

            if f == 0:
                print("Acabou o jogo!")
                break
         


def menu():
    while True:
        Show()
        opt = int(input('''Bem-vindos ao 'JOGO DOS FÓSFOROS'!
                             1- para jogar o modo mormal
                             2 -para jogar o modo computador
                             0 - para out da aplicação'''))

        if opt == 0:
            out()
            break

        elif opt == 1:
            normal()

        elif opt == 2:
            computador()

        else:
            print("ERRO")
            break

menu()