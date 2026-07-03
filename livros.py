class Livro:
    def __init__(self,titulo,autor,genero,preco,imagem, capa_dura=False, ebook=True):
        self.titulo=titulo
        self.autor=autor
        self.genero=genero
        self.preco=preco
        self.imagem=imagem

        self.capa_comum = True
        self.capa_dura = capa_dura
        self.ebook = ebook

catalogo = [
    Livro("A Hipotese do Amor", "Ali Hazelwood", "Romance", 46.26, "hipotese-amor.png", capa_dura=True, ebook=True),
    Livro("A Razão do Amor", "Ali Hazelwood", "Romance", 46.26, "razao-amor.png", ebook=True),
    Livro("Amor, Teoricamente", "Ali Hazelwood", "Romance", 46.26, "amor-teoricamente.png", capa_dura=True, ebook=True),
    Livro("No Fundo é Amor", "Ali Hazelwood", "Romance", 49.78, "no-fundo.png", capa_dura=False, ebook=True),
    Livro("Não é Amor", "Ali Hazelwood", "Romance", 43.14, "não-amor.png", capa_dura=False, ebook=True),
    Livro("Um Amor Problemático de Verão", "Ali Hazelwood", "Romance", 46.26, "amor-problematico.png", capa_dura=False, ebook=True),
    Livro("Odeio Te Amar", "Ali Hazelwood", "Romance", 36.78, "odeio-amar.png", capa_dura=False, ebook=True),
    Livro("Xeque-Mate", "Ali Hazelwood", "Romance", 43.14, "xeque-mate.png", capa_dura=False, ebook=True),
    Livro("Noiva", "Ali Hazelwood", "Romance e Fantasia", 46.26, "noiiva.png", capa_dura=True, ebook=True),
    Livro("Parceira", "Ali Hazelwood", "Romance e Fantasia", 46.26, "parceiraa.png", capa_dura=True, ebook=True),
    Livro("Jogo de Amor para Dois", "Ali Hazelwood", "Romance", 33.15, "jogo-amor.png", capa_dura=False, ebook=True),
    Livro("Assistente do Vilão", "Hannah Nicole Maehrer", "Romance e Fantasia", 47.19, "assistente-vilao.png", capa_dura=True, ebook=True),
    Livro("Aprendiz do Vilão", "Hannah Nicole Maehrer", "Romance e Fantasia", 48.58, "aprendiz-vilao.png", capa_dura=False, ebook=True),
    Livro("Aliada do Vilão", "Hannah Nicole Maehrer", "Romance e Fantasia", 43.55, "aliada-vilao.png", capa_dura=False, ebook=True),
    Livro("Uma Tempestade de Verão", "K. L. Walther", "Romance", 43.14, "tempestade-verao.png", capa_dura=False, ebook=True),
    Livro("Caraval", "Stephanie Garber", "Fantasia", 44.69, "caravall.png", capa_dura=False, ebook=True),
    Livro("Lendário", "Stephanie Garber", "Fantasia", 46.26, "lendarioo.png", capa_dura=False, ebook=True),
    Livro("Finale", "Stephanie Garber", "Fantasia", 44.96, "finalee.png", capa_dura=False, ebook=True),
    Livro("Melhor do Que Nos Filmes", "Lynn Painter", "Romance", 49.78, "melhor-filmes.png", capa_dura=False, ebook=True),
    Livro("Não é Como Nos Filmes", "Lynn Painter", "Romance", 48.51, "como-filmes.png", capa_dura=False, ebook=True),
    Livro("Patinando no amor", "Lynn Painter", "Romance", 49.78, "patinando-amor.png", capa_dura=False, ebook=True),
    Livro("Mil Vezes amor", "Lynn Painter", "Romance", 44.05, "mil-vezes.png", capa_dura=False, ebook=True),
    Livro("Apostando no Amor", "Lynn Painter", "Romance", 48.43, "apostando-amor.png", capa_dura=False, ebook=True),
    Livro("Sorte no Amor", "Lynn Painter", "Romance", 43.14, "sorte-amor.png", capa_dura=False, ebook=True),
    Livro("Confusões de Amor", "Lynn Painter", "Romance", 55.48, "confusoes-amor.png", capa_dura=False, ebook=True),
    Livro("Amor Por Engano", "Lynn Painter", "Romance", 43.14, "amor-engano.png", capa_dura=False, ebook=True),
    Livro("Powerless", "Lauren Roberts", "Fantasia", 70.05, "powerlesss.png", capa_dura=False, ebook=True),
    Livro("Reckless", "Lauren Roberts", "Fantasia", 45.14, "recklesss.png", capa_dura=False, ebook=True),
    Livro("Fearless", "Lauren Roberts", "Fantasia", 59.75, "fearlesss.png", capa_dura=False, ebook=True),
    Livro("Quarta Asa", "Rebecca Yarros", "Fantasia", 59.00, "quarta-asa.png", capa_dura=True, ebook=True),
    Livro("Chama de Ferro", "Rebecca Yarros", "Fantasia", 57.95, "chama-ferro.png", capa_dura=True, ebook=True),
    Livro("Tempestade de Ônix", "Rebecca Yarros", "Fantasia", 60.00, "tempestade-onix.png", capa_dura=True, ebook=True),
    Livro("Era Uma Vez um Coração Partido", "Stephanie Garber", "Fantasia", 54.47, "era-partido.png", capa_dura=False, ebook=True),
    Livro("A Balada dos Felizes para Nunca", "Stephanie Garber", "Fantasia", 43.10, "balada-nunca.png", capa_dura=False, ebook=True),
    Livro("A Maldição do Verdadeiro Amor", "Stephanie Garber", "Fantasia", 47.55, "maldicao-verdadeiro.png", capa_dura=False, ebook=True),
    Livro("Estilhaça-me", "Tahereh Mafi", "Distópia e Romance", 45.44, "estilhaça-me.png", capa_dura=True, ebook=True),
    Livro("Liberta-me", "Tahereh Mafi", "Distópia e Romance", 45.92, "liberta-me.png", capa_dura=True, ebook=True),
    Livro("Incendeia-me", "Tahereh Mafi", "Distópia e Romance", 48.90, "incendeia-me.png", capa_dura=True, ebook=True),
    Livro("Restaura-me", "Tahereh Mafi", "Distópia e Romance", 43.34, "restaura-me.png", capa_dura=False, ebook=True),
    Livro("Desafia-me", "Tahereh Mafi", "Distópia e Romance", 43.37, "desafia-me.png", capa_dura=False, ebook=True),
    Livro("Imagina-me", "Tahereh Mafi", "Distópia e Romance", 46.87, "imagina-me.png", capa_dura=False, ebook=True),
    Livro("Divinos Rivais", "Rebecca Ross", "Fantasia e Romance", 46.45, "divinos-rivais.png", capa_dura=True, ebook=True),
    Livro("Promessas Cruéis", "Rebecca Ross", "Fantasia e Romance", 46.45, "promessas-crueis.png", capa_dura=True, ebook=True),        
]