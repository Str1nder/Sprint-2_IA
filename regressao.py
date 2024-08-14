# regressao.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import matplotlib

matplotlib.use('Agg')  

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
        'df': df,
        'X_test': X_test,
        'pred_receita': pred_receita,
        'pred_despesa': pred_despesa,
        'intervalo_confianca_receita': intervalo_confianca_receita,
        'intervalo_confianca_despesa': intervalo_confianca_despesa,
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
    buf = io.BytesIO()
    plt.savefig(buf, format='svg')
    buf.seek(0)
    graph = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return graph
