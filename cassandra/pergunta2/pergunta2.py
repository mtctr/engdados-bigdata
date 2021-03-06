#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyspark.sql import SparkSession

# Cria a sessão.
spark = SparkSession.builder.appName("Pergunta2").getOrCreate()

# Gera um DataFrame com os resultados da eleição de 2014.
eleicoesDF = spark.read.format("org.apache.spark.sql.cassandra").\
    options(keyspace="eleicoes", table="resultados2014").\
    load()

# Obtém o código dos candidatos eleitos e suas cidades.
codigos = eleicoesDF.\
    filter(eleicoesDF['codigo_sit_cand_tot'] < 4).\
    select('sq_candidato', 'codigo_municipio').\
    distinct()

# Gera um DataFrame com os dados dos candidatos.
candidatosDF = spark.read.format("org.apache.spark.sql.cassandra").\
    options(keyspace="eleicoes", table="candidatos2014").\
    load()

# Obtém apenas as informações úteis.
informacoes = candidatosDF.select('sequencial_candidato', 'sigla_partido')

# Gera um DataFrame com os dados dos pibs.
pibsDF = spark.read.format("org.apache.spark.sql.cassandra").\
    options(keyspace="eleicoes", table="pibs").\
    load()

# Obtém os PIBS de acima de R$ 70.000,00;
pibs = pibsDF.\
    filter(pibsDF['pib_percapita'] > 70000.0).\
    select('uf', 'cidade', 'cod_tse')

# Faz o join dos eleitos e das informações (partido).
dados_eleitos = codigos.join(informacoes, codigos['sq_candidato'] == informacoes['sequencial_candidato'], 'inner')

# Faz o join dos eleitos e das informações.
final = dados_eleitos.join(pibs, dados_eleitos['codigo_municipio'] == pibs['cod_tse'], 'inner')

# Obtém as respostas desejadas (conta as entradas para cada coluna).
res_partidos = final.groupby(['sigla_partido']).count()

# Armazena o resultado no HDFS.
res_partidos.write.format("csv").save("hdfs://dricardo-master:9000/user/engdados/res_partidos.csv")

print 'Encerrado com sucesso.'
