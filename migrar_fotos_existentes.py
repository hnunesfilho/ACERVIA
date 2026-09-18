# scripts/migrar_fotos_existentes.py
# Execute este script UMA VEZ para copiar as fotos já cadastradas
# (que estão com caminho completo antigo) para a pasta interna do projeto,
# e atualizar o banco para guardar apenas o nome do novo arquivo.

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import Connection
from utils.gerenciador_fotos import salvar_foto


def migrar():
    db = Connection()
    exemplares = db.execute(
        "SELECT id_exemplar, foto_path FROM exemplares WHERE foto_path IS NOT NULL", fetch=True
    )

    if not exemplares:
        print("Nenhum exemplar com foto encontrado para migrar.")
        return

    migrados = 0
    nao_encontrados = 0

    for ex in exemplares:
        caminho_antigo = ex["foto_path"]

        # Se já parece ser apenas um nome de arquivo (sem barra), pula —
        # provavelmente já foi migrado antes.
        if os.sep not in caminho_antigo and "/" not in caminho_antigo:
            continue

        if not os.path.exists(caminho_antigo):
            print(f"[AVISO] Arquivo não encontrado, exemplar {ex['id_exemplar']}: {caminho_antigo}")
            nao_encontrados += 1
            continue

        novo_nome = salvar_foto(caminho_antigo)
        db.execute(
            "UPDATE exemplares SET foto_path = %s WHERE id_exemplar = %s",
            (novo_nome, ex["id_exemplar"])
        )
        migrados += 1
        print(f"Migrado exemplar {ex['id_exemplar']}: {caminho_antigo} -> {novo_nome}")

    print(f"\nConcluído. {migrados} foto(s) migrada(s). {nao_encontrados} arquivo(s) não encontrado(s).")


if __name__ == "__main__":
    migrar()