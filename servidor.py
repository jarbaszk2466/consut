from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Carrega o Excel uma vez para ser ultra rápido
def carregar_dados():
    if os.path.exists('produtos.xls'):
        # header=None pois o arquivo pode não ter nomes de colunas padrão
        return pd.read_excel('produtos.xls', header=None)
    return None

df_produtos = carregar_dados()

@app.route('/consulta/<barcode>')
def api_consulta(barcode):
    global df_produtos
    try:
        if df_produtos is None:
            df_produtos = carregar_dados()
            if df_produtos is None:
                return jsonify({"erro": "Arquivo nao encontrado"}), 500

        barcode_procurado = str(barcode).strip()

        # Busca na Coluna D (índice 3)
        resultado = df_produtos[df_produtos[3].astype(str).str.contains(barcode_procurado)]

        if not resultado.empty:
            row = resultado.iloc[0]
            # Nome na Coluna G (índice 6)
            nome = str(row[6]).strip().upper()
            if nome == "NAN": nome = "PRODUTO SEM NOME"
            
            # Preço automático (testando colunas comuns)
            preco = 0.0
            for col_p in [25, 24, 7, 8]:
                if col_p < len(row):
                    try:
                        val = float(str(row[col_p]).replace(',', '.'))
                        if val > 0:
                            preco = val
                            break
                    except: continue
            
            return jsonify({"nome": nome, "preco": preco}), 200
        
        return jsonify({"erro": "Nao encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    print("Servidor 'Nossa Conveniencia' ON!")
    app.run(host='0.0.0.0', port=5000)