"""
Propósito: Dividir as questões por padrão visual vertical de 3 faixas no penúltimo pixel da direita.
Padrão:
  - Faixa 1: 6px RGB(35, 31, 32) (margem 3 a 9 px)
  - Faixa 2: 4px RGB(211, 210, 210) (margem 1 a 7 px)
  - Faixa 3: 2px RGB(35, 31, 32) (margem 0 a 5 px)
Corte: 21 pixels acima do início do padrão (mantendo esses 21px no topo do novo recorte).
"""

from PIL import Image
import os

def cor_combina(pixel, cor_alvo, tolerancia=15):
    """
    Verifica se a cor de um pixel combina com a cor alvo considerando uma tolerância.
    """
    if len(pixel) == 4:  # RGBA
        r, g, b, _ = pixel
    else:  # RGB
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_padrao_vertical(imagem, tolerancia=15):
    """
    Encontra posições onde o padrão visual vertical de 3 faixas ocorre
    no penúltimo pixel da direita (largura - 2).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    x = largura - 5  # Penúltimo pixel da direita
    
    # Cores do padrão (RGB 0-255)
    cor1 = (35, 31, 32)
    cor2 = (211, 210, 210)
    cor3 = (35, 31, 32)
    
    posicoes_corte = []
    y = 0
    
    # Percorre de cima para baixo
    while y < altura - 20:  # Garante espaço mínimo para verificar a sequência
        # 1. Mede o tamanho da primeira faixa (cor1)
        h1 = 0
        while (y + h1) < altura and cor_combina(pixels[x, y + h1], cor1, tolerancia):
            h1 += 1
            
        # Verifica faixa 1: 6px nominal (3 a 9px com margem)
        if 3 <= h1 <= 9:
            # 2. Mede o tamanho da segunda faixa (cor2)
            y2 = y + h1
            h2 = 0
            while (y2 + h2) < altura and cor_combina(pixels[x, y2 + h2], cor2, tolerancia):
                h2 += 1
                
            # Verifica faixa 2: 4px nominal (1 a 7px com margem)
            if 1 <= h2 <= 7:
                # 3. Mede o tamanho da terceira faixa (cor3)
                y3 = y2 + h2
                h3 = 0
                while (y3 + h3) < altura and cor_combina(pixels[x, y3 + h3], cor3, tolerancia):
                    h3 += 1
                    
                # Verifica faixa 3: 2px nominal (0 a 5px com margem, aceita no mínimo 0 se muito fina)
                if 0 <= h3 <= 5 and (h1 + h2 + h3) > 0:
                    # Padrão encontrado no Y inicial da primeira faixa!
                    posicao_corte = max(0, y - 21)  # Corta 21px acima do início do padrão
                    posicoes_corte.append(posicao_corte)
                    print(f"Padrão encontrado em y={y} (alturas: {h1}px, {h2}px, {h3}px). Cortando em y={posicao_corte}")
                    
                    # Avança o loop pulando todo o padrão para evitar detecções duplicadas
                    y += (h1 + h2 + max(h3, 1))
                    continue
        
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando nas posições identificadas pelo padrão
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao_vertical(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
        
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
        
    # Corta a seção final após o último ponto de corte
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "colunas"           # Substitua pelo nome da pasta de saída
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    print("Divisão concluída!")