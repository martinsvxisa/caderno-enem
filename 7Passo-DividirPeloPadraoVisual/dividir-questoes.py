from PIL import Image
import os

def cor_similar(cor_pixel, cor_alvo, tolerancia=15):
    """
    Verifica se a cor do pixel está dentro da tolerância em relação à cor alvo (RGB)
    """
    return all(abs(c1 - c2) <= tolerancia for c1, c2 in zip(cor_pixel[:3], cor_alvo))

def validar_faixa(pixels, x, y_inicio, altura_esperada, cor_alvo, margem_altura=1):
    """
    Verifica se a partir de y_inicio existe uma faixa da cor_alvo com a altura dentro da margem
    Retorna a altura real encontrada (se válida) ou 0 se não for válida.
    """
    altura_atual = 0
    # Percorre até a altura máxima permitida
    max_altura = altura_esperada + margem_altura
    min_altura = max(1, altura_esperada - margem_altura)
    
    while altura_atual < max_altura:
        y_atual = y_inicio + altura_atual
        if y_atual >= pixels_altura:
            break
            
        pixel = pixels[x, y_atual]
        if cor_similar(pixel, cor_alvo):
            altura_atual += 1
        else:
            break

    if min_altura <= altura_atual <= max_altura:
        return altura_atual
    return 0

def encontrar_padrao_vertical(imagem, tolerancia=20):
    """
    Encontra o padrão vertical (6px, 4px, 2px) no penúltimo pixel da direita com margem de 1px
    """
    global pixels_altura
    largura, altura = imagem.size
    pixels_altura = altura
    pixels = imagem.load()
    
    # Cores do padrão (RGB 0-255)
    cor_f1 = (35, 31, 32)    # 6px (5 a 7)
    cor_f2 = (211, 210, 210) # 4px (3 a 5)
    cor_f3 = (35, 31, 32)    # 2px (1 a 3)
    
    x = largura - 2  # Penúltimo pixel da direita
    posicoes_corte = []
    
    y = 0
    while y < altura - 12:
        # Tenta validar a primeira faixa (6px +/- 1px)
        h1 = validar_faixa(pixels, x, y, altura_esperada=6, cor_alvo=cor_f1, margem_altura=1)
        if h1 > 0:
            # Tenta validar a segunda faixa (4px +/- 1px) logo após a primeira
            h2 = validar_faixa(pixels, x, y + h1, altura_esperada=4, cor_alvo=cor_f2, margem_altura=1)
            if h2 > 0:
                # Tenta validar a terceira faixa (2px +/- 1px) logo após a segunda
                h3 = validar_faixa(pixels, x, y + h1 + h2, altura_esperada=2, cor_alvo=cor_f3, margem_altura=1)
                if h3 > 0:
                    # Padrão completo encontrado!
                    # Corta 21 pixels acima do início do padrão
                    posicao_corte = max(0, y - 21)
                    posicoes_corte.append(posicao_corte)
                    
                    altura_total_padrao = h1 + h2 + h3
                    print(f"Padrão encontrado em y={y} (faixas: {h1}px, {h2}px, {h3}px). Cortando em y={posicao_corte}")
                    
                    # Avança além do padrão encontrado para evitar re-detecção
                    y += altura_total_padrao
                    continue
        
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando com base no padrão encontrado
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao_vertical(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} pontos de corte")
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
    
    # Salva a última parte (do último corte até o fim da imagem)
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