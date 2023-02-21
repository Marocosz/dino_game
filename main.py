import pygame
from pygame.locals import *
from sys import exit
import os  # Biblioteca a ver com caminhos (paths)
from random import randrange
from random import choice

pygame.init()
pygame.mixer.init()  # Iniciador dos sons

diretorio_principal = os.path.dirname(__file__)  # Alocar na variável o path onde está o arquivo
diretorio_imagens = os.path.join(diretorio_principal, 'sprites')  # Alocar junto ao diretório principal outro diretório
                                                                  # de acordo com oque está no parametro
diretorio_sons = os.path.join(diretorio_principal, 'sons')
# Uteis para tal código funcionar em outras máquinas

LARGURA = 640
ALTURA = 480

BRANCO = (255, 255, 255)

tela = pygame.display.set_mode((LARGURA, ALTURA))

icone = pygame.image.load(os.path.join(diretorio_imagens, 'icon.png'))  # Carregar icone
pygame.display.set_icon(icone)  # Adicionar icone da janela

pygame.display.set_caption('Dino Game')

sprite_sheet = pygame.image.load(os.path.join(diretorio_imagens, 'dinoSpritesheet.png')).convert_alpha()
# Carregando o Sprite Sheet
# .convert_alpha() serve para imagens sem fundos não ter problema (png's)

som_colisao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'death_sound.wav'))  # carregando o som de colisao
som_colisao.set_volume(1)

som_pontuacao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'score_sound.wav'))  # Carregando som de pontuação
som_pontuacao.set_volume(1)

colidiu = False

escolha_obstaculo = choice([0, 1])  # Aleatorização inicial do objeto que vai aparecer

pontuacao = 0  # Pontuação inicial

velocidade_jogo = 10  # Velocidade inicial de momvimento dos objetos


def exibe_mensagem(msg, tamanho, cor):
    fonte = pygame.font.SysFont('comicsansms', tamanho, bold=True, italic=False)
    mensagem = f'{msg}'
    texto_formatado = fonte.render(mensagem, True, cor)

    return texto_formatado


def reiniciar_jogo():  # Função para reiniciar todos atributos como se fosse primeiro game
    global pontuacao, velocidade_jogo, colidiu, escolha_obstaculo  # Definir que a alteração será global oa usar a func
    pontuacao = 0
    velocidade_jogo = 10
    colidiu = False
    voador.rect.x = LARGURA
    cacto.rect.x = LARGURA
    dino.rect.y = ALTURA - 64 - (96/2)
    dino.pule = False



class Dino(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.som_pulo = pygame.mixer.Sound(os.path.join(diretorio_sons, 'jump_sound.wav'))  # Add som do pulo
        self.som_pulo.set_volume(1)

        self.imagens_dinossauro = []
        for c in range(3):
            img = sprite_sheet.subsurface((c * 32, 0), (32, 32))
            img = pygame.transform.scale(img, (32 * 3, 32 * 3))
            self.imagens_dinossauro.append(img)
            # sprite_sheet.subsurface | serve para pegarmos cada sprite dentro do sprite sheet
            # For para pegar cada sprite dentro da sprite sheet e alocar dentro de uma lista

        self.posicao_y_inicial = ALTURA - 64 - (96/2)
        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]  # Definir que cada sprite dentro da lista é uma imagem
        self.rect = self.image.get_rect()  # Carregar o retangulo de cada sprite dentro da lista
        self.mask = pygame.mask.from_surface(self.image)  # Criação da mascára de colisão por pixel do objeto
        self.rect.center = (100, self.posicao_y_inicial)  # Definir aonde aparecerá esta sprite na tela

        self.pule = False

    def pular(self):  # Função para ativar a animação pular
        self.pule = True
        self.som_pulo.play()  # Ativar som pulo ao pular

    def update(self):

        if self.pule:  # If para fazer o dino subir 20 px quando self.pule == True
            if self.rect.y <= 200:  # Quando a altura do dino chegar a 200, pule vai ser false
                self.pule = False
            self.rect.y -= 20  # Se pule = True: subir 20 px em y
        else:  # se pule == False:
            if self.rect.y < self.posicao_y_inicial:  # se a altura for menor que a inicial, aumentar +20 px em y
                                                      # ou seja, fará ele descer ao chegar aonde queremos
                self.rect.y += 20
            else:
                self.rect.y = self.posicao_y_inicial  # Se não for menor, continue onde está

        # Função para atualizar as sprites que estão dentro da lista, uma de cada vez
        if self.index_lista > 2:
            self.index_lista = 0
        self.index_lista += 0.25  # 0.25 para não ir tão rapido
        self.image = self.imagens_dinossauro[int(self.index_lista)]
        # int(self.index_lista) pois só exist indices de listas inteiros


class Nuvens(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((7 * 32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))
        self.rect = self.image.get_rect()
        self.rect.y = randrange(50, 200, 50)  # Definindo sua localização em Y com randrange(inicio, final, passo)
        self.rect.x = LARGURA - randrange(30, 300, 90)

    def update(self):
        # Função para atualizar as nuvens (animação de loop de um lado pro outro)
        if self.rect.topright[0] < 0:
            # Quando a parte direita seprior estiver em X0: usamos [0] pois topright é uma tupla (X, Y) e queremos X
            self.rect.x = LARGURA  # Resetar x
            self.rect.y = randrange(50, 200, 50)  # aleaotizar altura da nuvem assim como a cima
        self.rect.x -= velocidade_jogo


class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):  # parametro: pos_x -> Para distribuirmos o chão em toda tela quando criarmos o objeto
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((6 * 32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32 * 2, 32 * 2))
        self.rect = self.image.get_rect()
        self.rect.y = ALTURA - 64
        self.rect.x = pos_x * 64

    def update(self):
        # Função de atualização do chão
        if self.rect.topright[0] < 0:  # quando o lado direito superior estiver em X0:
            self.rect.x = LARGURA  # O retangulo da sprite no eixo X voltaram pro final
        self.rect.x -= 10  # diminuíra 10 a cada iteração
        # OBS: Não usamos a velocidade_jogo no chão por causa


class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((5*32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32*2, 32*2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)  # Criação da mascára de colisão por pixel do objeto
        self.rect.center = (LARGURA,  ALTURA - 64)
        self.rect.x = LARGURA

        self.escolha = escolha_obstaculo

    def update(self):  # Sistema para loop
        if self.escolha == 0:  # Sistema para aleatorizar qual obstaculo aparecerá
            if self.rect.topright[0] < 0:
                self.rect.x = LARGURA
            self.rect.x -= velocidade_jogo


class Voador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.imagens_voador = []
        for c in range(3, 5):  # Adicionando as imagens do voador na lista
            img = sprite_sheet.subsurface((c*32, 0), (32, 32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_voador.append(img)

        self.index_lista = 0
        self.image = self.imagens_voador[self.index_lista]
        self.mask = pygame.mask.from_surface(self.image)  # Criação da mascára de colisão por pixel do objeto
        self.rect = self.image.get_rect()
        self.rect.center = (LARGURA, 300)
        self.rect.x = LARGURA

        self.escolha = escolha_obstaculo

    def update(self):  # Sistema para loop
        if self.escolha == 1:  # Sistema para aleatorizar qual obstaculo aparecerá
            if self.rect.topright[0] < 0:
                self.rect.x = LARGURA
            self.rect.x -= velocidade_jogo

            # Função para atualizar as sprites que estão dentro da lista, uma de cada vez
            if self.index_lista > 1:
                self.index_lista = 0
            self.index_lista += 0.25  # 0.25 para não ir tão rapido
            self.image = self.imagens_voador[int(self.index_lista)]
            # int(self.index_lista) pois só exist indices de listas inteiros


todas_as_sprites = pygame.sprite.Group()  # Criação do grupo de sprites

dino = Dino()
todas_as_sprites.add(dino)  # Adicionando as sprites Dino

for i in range(4):  # Criando 4 nuvens
    nuvem = Nuvens()
    todas_as_sprites.add(nuvem)

for i in range(22):  # 22 Número suficiente para cobrir o chão
    chao = Chao(i)  # parametro pos_x: i -> ou seja, a cada for, teremos um sprite chão em um lugar difernte da tela
                    # 0 * 64(largura do sprite) na posição x, 1 * 64, 2 * 64....
    todas_as_sprites.add(chao)

cacto = Cacto()
todas_as_sprites.add(cacto)

voador = Voador()
todas_as_sprites.add(voador)

grupo_obstaculos = pygame.sprite.Group()  # Grupo dos obstaculos do dino
grupo_obstaculos.add(cacto)
grupo_obstaculos.add(voador)

relogio = pygame.time.Clock()  # Definição do definidor de fps
while True:
    relogio.tick(30)  # Definindo 30 fps
    tela.fill(BRANCO)  # Pintando a tela de fundo
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

        if event.type == KEYDOWN:
            if event.key == K_SPACE and not colidiu:
                if dino.rect.y != dino.posicao_y_inicial:  # Se a altura do dinossauro nao for a do chão (inicial)
                                                           # Não poderá usar 'space' novamente
                    pass
                else:
                    dino.pular()

            if event.key == K_r and colidiu:
                reiniciar_jogo()

    colisoes = pygame.sprite.spritecollide(dino, grupo_obstaculos, False, pygame.sprite.collide_mask)
    # Variável da colisa conforme o tipo
    # (objeto princiapl,  grupo_dos_objetos_que_vai_ser_colidido,True or False para desaparecer, tipo_de_colisao)

    todas_as_sprites.draw(tela)  # Carregar o grupo de sprites

    if cacto.rect.topright[0] <= 0 or voador.rect.topright[0] <= 0:  # Reiniciar variavel de aleatorização do obstaculo
        escolha_obstaculo = choice([0, 1])                           # Toda vez q um obstaculo passar pelo limite
        cacto.rect.x = LARGURA  # Reiniciando a posição dos obstaculos
        voador.rect.x = LARGURA
        cacto.escolha = escolha_obstaculo  # Atualizando a variavel dentro da class
        voador.escolha = escolha_obstaculo

    if colisoes and not colidiu:  # If para pausar ao colidir
        colidiu = True
        som_colisao.play()

    if colidiu:  # Se colidiu = True passar e não atualizar a tela
        if pontuacao % 100 == 0:  # IF para quebrar bug de tocar infinitamente caso colidir numa pontuação divisivel
            pontuacao +=1         # por 100

        game_over = exibe_mensagem('GAME OVER', 40, (0, 0, 0))  # Criando msg de game over
        tela.blit(game_over, (200, 200))  # Fazendo ela aparecer na condição colidiu
        pressione_msg = exibe_mensagem('Pressione "R" para reiniciar', 15, (0, 0, 0)) # Criando msg de reiniciar
        tela.blit(pressione_msg, (220, 250))  # Fazendo ela aparecer na condição colidiu


    else:
        pontuacao += 0.5
        todas_as_sprites.update()  # Atualizar o grupo de sprites a cada iteravel do loop
        texto_pontuacao = exibe_mensagem(int(pontuacao), 30, (0, 0, 0))

    if pontuacao != 0 and pontuacao % 100 == 0:
        som_pontuacao.play()
        if velocidade_jogo >= 23:
            velocidade_jogo += 0
        else:
            velocidade_jogo += 1

    tela.blit(texto_pontuacao, (530, 20))
    pygame.display.flip()
