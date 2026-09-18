# utils/gerenciador_fotos.py

import os
import shutil
import uuid

# Pasta fixa dentro do projeto onde todas as fotos de exemplares ficam guardadas.
# Como está dentro da própria estrutura do Acervia, ao copiar a pasta do projeto
# para outra máquina, as fotos vão junto.
PASTA_FOTOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fotos_exemplares")


def garantir_pasta_fotos():
    """Cria a pasta de fotos caso ainda não exista."""
    os.makedirs(PASTA_FOTOS, exist_ok=True)


def salvar_foto(caminho_origem):
    """
    Copia a foto escolhida pelo usuário para a pasta interna do projeto,
    gerando um nome único de arquivo para evitar sobrescrever fotos
    de exemplares diferentes que tenham o mesmo nome original.

    Retorna apenas o NOME do arquivo salvo (não o caminho completo),
    que é o que deve ser gravado na coluna foto_path do banco de dados.
    """
    garantir_pasta_fotos()

    extensao = os.path.splitext(caminho_origem)[1].lower()
    nome_unico = f"{uuid.uuid4().hex}{extensao}"
    caminho_destino = os.path.join(PASTA_FOTOS, nome_unico)

    shutil.copy2(caminho_origem, caminho_destino)
    return nome_unico


def caminho_completo_foto(nome_arquivo):
    """
    Monta o caminho completo de uma foto a partir do nome salvo no banco.
    Usado sempre que for necessário abrir/exibir a imagem na tela.
    """
    if not nome_arquivo:
        return None
    return os.path.join(PASTA_FOTOS, nome_arquivo)


def remover_foto(nome_arquivo):
    """Remove o arquivo físico da pasta de fotos, se existir."""
    if not nome_arquivo:
        return
    caminho = caminho_completo_foto(nome_arquivo)
    if caminho and os.path.exists(caminho):
        try:
            os.remove(caminho)
        except Exception:
            pass