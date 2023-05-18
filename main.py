# Importando as Bibliotecas
import zipfile
import pandas as pd

# Descompactando o arquivo .zip
zip_path = 'dados.zip'
zip_file = zipfile.ZipFile(zip_path)
zip_file.extractall()

# Lendo os arquivos .csv
origem_dados_csv = 'origem-dados.csv'
tipos_csv = 'tipos.csv'

dados_origem = pd.read_csv(origem_dados_csv)
tipos = pd.read_csv(tipos_csv)

# Tratando os dados (Filtrando por status CRITICO, ordenando por data e adicionando o nome do tipo)
dados_origem['created_at'] = pd.to_datetime(dados_origem['created_at'])
dados_critico = dados_origem[dados_origem['status'] == 'CRITICO']
dados_critico_ordenado = dados_critico.sort_values(by='created_at')
dados_critico_ordenado['tipo_nome'] = dados_critico_ordenado['tipo'].map(
    tipos.set_index('id')['nome'])

print(dados_critico_ordenado.head())

# Criando o arquivo .sql (Criando a tabela)
sql_file = open('dados.sql', 'w')

sql_file.write(''' 
CREATE TABLE dados_finais (
        created_at DATE,
        product_code VARCHAR(255),
        customer_code VARCHAR(255),
        status VARCHAR(255),
        tipo VARCHAR(255),
        tipo_nome VARCHAR(255)
);

''')

# Inserindo os dados no arquivo .sql 
for index, row in dados_critico_ordenado.iterrows():
    sql_file.write('''
INSERT INTO dados_finais (
        created_at,
        product_code,
        customer_code,
        status,
        tipo,
        tipo_nome
    ) VALUES ('{}', '{}', '{}', '{}', '{}', '{}');\n'''.format(
        row['created_at'],
        row['product_code'],
        row['customer_code'],
        row['status'],
        row['tipo'],
        row['tipo_nome']
    )
    )


# Query que retorna por dia a quantidade de itens agrupados pelo tipo
sql_file.write('''
SELECT 
    DATE(created_at) as data,
    tipo_nome as tipo,
    COUNT('tipo') as contagem
FROM dados_finais 
GROUP BY 
    data,
    tipo_nome
ORDER BY contagem DESC;
''')

