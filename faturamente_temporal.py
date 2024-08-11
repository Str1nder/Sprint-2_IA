from flask import Flask, request, jsonify
from flask_cors import CORS  
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import io
import base64
import matplotlib

matplotlib.use('Agg')  # Configura o backend para modo não interativo

app = Flask(__name__)
CORS(app)  

# Regressao linear para previsao de despesas e receitas
def modelo_faturamento(df):
    df['Datas'] = pd.to_datetime(df['Datas'], format='%d/%m/%Y')
    df = df.drop(['Unnamed: 0'], axis=1)

    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    scaler = MinMaxScaler()
    df_normalized = df.copy()
    df_normalized[num_cols] = scaler.fit_transform(df[num_cols])

    X = df_normalized[['Gastos com a previdência', 'Salários', 'Outras obrigações']]
    y_receita = df_normalized['Receita bruta']
    y_despesa = df_normalized['Despesas']

    X_train, X_test, y_receita_train, y_receita_test, y_despesa_train, y_despesa_test = train_test_split(X, y_receita, y_despesa, test_size=0.2, shuffle=False)

    model_receita = LinearRegression().fit(X_train, y_receita_train)
    model_despesa = LinearRegression().fit(X_train, y_despesa_train)

    pred_receita = model_receita.predict(X_test)
    pred_despesa = model_despesa.predict(X_test)

    desvio_receita = np.std(y_receita_test - pred_receita)
    desvio_despesa = np.std(y_despesa_test - pred_despesa)

    intervalo_confianca_receita = 1.96 * desvio_receita
    intervalo_confianca_despesa = 1.96 * desvio_despesa

    pred = {
        'df' : df,
        'X_test' : X_test,
        'pred_receita' : pred_receita,
        'pred_despesa' : pred_despesa,
        'intervalo_confianca_receita' : intervalo_confianca_receita,
        'intervalo_confianca_despesa' : intervalo_confianca_despesa,
    }

    return pred


def grafico_linha(df, y, X_test, pred, intervalo_confianca):

    plt.figure(figsize=(12, 6))
    plt.plot(df['Datas'], df[y], label=f'{y} Real', color='blue')
    plt.plot(df['Datas'].iloc[X_test.index], pred, label=f'{y} Prevista', linestyle='--', color='red')
    plt.fill_between(df['Datas'].iloc[X_test.index], pred - intervalo_confianca, pred + intervalo_confianca, color='green', alpha=0.2)
    plt.xlabel('Data')
    plt.ylabel('Valor')
    plt.title(f'{y} Reais vs {y} Previstas com Intervalos de Confiança')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='svg')
    buf1.seek(0)
    graph = base64.b64encode(buf1.read()).decode('utf-8')
    plt.close()
    return graph

# Receita x Despesa
@app.route('/faturamento', methods=['POST'])
def faturamento():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_excel(file)
        
        pred = modelo_faturamento(df)

        img2_str = grafico_linha(df, 'Receita bruta' , pred['X_test'], pred['pred_receita'], pred['intervalo_confianca_receita'])
        img3_str = grafico_linha(df, 'Despesas' ,pred['X_test'], pred['pred_despesa'], pred['intervalo_confianca_despesa'])

        # Gráfico 1
        plt.figure(figsize=(12, 6))
        plt.plot(df['Datas'], df['Receita bruta'], label='Receita Bruta Real', color='blue')
        plt.plot(df['Datas'].iloc[pred['X_test'].index], pred['pred_receita'], label='Receita Bruta Prevista', linestyle='--', color='green')
        plt.fill_between(df['Datas'].iloc[pred['X_test'].index], pred['pred_receita'] - pred['intervalo_confianca_receita'], pred['pred_receita'] + pred['intervalo_confianca_receita'], color='blue', alpha=0.2)
        plt.plot(df['Datas'], df['Despesas'], label='Despesas Reais', color='red')
        plt.plot(df['Datas'].iloc[pred['X_test'].index], pred['pred_despesa'], label='Despesas Previstas', linestyle='--', color='purple')
        plt.fill_between(df['Datas'].iloc[pred['X_test'].index], pred['pred_despesa'] - pred['intervalo_confianca_despesa'], pred['pred_despesa'] + pred['intervalo_confianca_despesa'], color='red', alpha=0.2)
        plt.xlabel('Data')
        plt.ylabel('Valor')
        plt.title('AAAAAAReceita e Despesas Reais vs Previstas com Intervalos de Confiança')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf1 = io.BytesIO()
        plt.savefig(buf1, format='svg')
        buf1.seek(0)
        img1_str = base64.b64encode(buf1.read()).decode('utf-8')
        plt.close()

        # # Gráfico 2
        # plt.figure(figsize=(12, 6))
        # plt.plot(df['Datas'], df['Receita bruta'], label='Receita Bruta Real', color='blue')
        # plt.plot(df['Datas'].iloc[X_test.index], pred_receita, label='Receita Bruta Prevista', linestyle='--', color='blue')
        # plt.fill_between(df['Datas'].iloc[X_test.index], pred_receita - intervalo_confianca_receita, pred_receita + intervalo_confianca_receita, color='blue', alpha=0.2)
        # plt.xlabel('Data')
        # plt.ylabel('Valor')
        # plt.title('Receita Bruta Real vs Prevista com Intervalos de Confiança')
        # plt.legend()
        # plt.xticks(rotation=45)
        # plt.tight_layout()
        # buf2 = io.BytesIO()
        # plt.savefig(buf2, format='svg')
        # buf2.seek(0)
        # img2_str = base64.b64encode(buf2.read()).decode('utf-8')
        # plt.close()

        # # Gráfico 3
        # plt.figure(figsize=(12, 6))
        # plt.plot(df['Datas'], df['Despesas'], label='Despesas Reais', color='red')
        # plt.plot(df['Datas'].iloc[X_test.index], pred_despesa, label='Despesas Previstas', linestyle='--', color='blue')
        # plt.fill_between(df['Datas'].iloc[X_test.index], pred_despesa - intervalo_confianca_despesa, pred_despesa + intervalo_confianca_despesa, color='red', alpha=0.2)
        # plt.xlabel('Data')
        # plt.ylabel('Valor')
        # plt.title('Despesas Reais vs Previstas com Intervalos de Confiança')
        # plt.legend()
        # plt.xticks(rotation=45)
        # plt.tight_layout()
        # buf3 = io.BytesIO()
        # plt.savefig(buf3, format='svg')
        # buf3.seek(0)
        # img3_str = base64.b64encode(buf3.read()).decode('utf-8')
        # plt.close()

        response = {
            'graphs': [
                {'url': f'data:image/svg+xml;base64,{img1_str}'},
                {'url': f'data:image/svg+xml;base64,{img2_str}'},
                {'url': f'data:image/svg+xml;base64,{img3_str}'}
            ]
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


app.run(debug=True)