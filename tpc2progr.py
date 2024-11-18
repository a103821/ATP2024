import random


print(''' ++ BEM-VINDO AO NUMGUESS ++
         ----------------------------
         ----------------------------
         --COMPUTADOR (Adivinha o número que o disposivo pensou)---------------------------------------
         ----------------------------------------------------------------------------------------------
         --NORMAL (Pretendes que o computador adivinhe o teu número? esta é a opção perfeita para ti!)-
      

         --------SAIR----------------------------------------------------------------------------------''')

i = int(input('''O que quer jogar?
              Opção 1- COMPUTADOR
              Opção 2- NORMAL
              Opção 0- SAIR'''))

#Opção 0- Sair
if i == 0:
    print("Adeus!")

#Opção 1- MODO COMPUTADOR
elif i == 1:
    e = 0
    num = random.randint(0,101)

    while True:
        quest = int(input("EM QUE NÚMERO O PC ESTÁ A PENSAR?"))
        e += 1

        if quest == num:
            print(f"WOW! Acertaste no número! Em {e} tentativa(S)!")
            break
    
        elif quest > num:
            print(f"Quase! O número que pensou foi {quest}, o que eu pensei é menor.")

        else:
            print(f"Quase! O número que pensou foi {quest}, o que eu pensei é maior.")

#opção 2- MODO NORMAL

elif i == 2:
    e = 0
    menor = 0
    maior = 100
    print("Pense num número de 0 e 100!")

    while True:

        meio = (maior+menor)//2
        print(f" O seu número é {meio}?")
     
        res = input("Acertou? É Maior? É Menor?").lower()
        e +=1

        if res == "acertou":
            print(f"Acertei em apenas {e} tentativas!")
            break
                    
        elif res== "maior":
            menor = meio + 1

        elif res== "menor":
            maior = meio - 1

        else:
            print(f"Resposta inválida, tente outra vez ;-;")