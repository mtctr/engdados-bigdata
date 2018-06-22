from pyspark.sql import SparkSession as spark

#configuração do spark
spark.builder.config('spark.jars.packages','org.mongodb.spark:mongo-spark-connector_2.11:2.2.0' ).getOrCreate()


#-------------------------------------------------------------------------
#COMANDOS PARA RODAR NA SHELL DO PYSPARK

#conexão com a collection de candidatos
spark_candidatos = spark \
    .builder \
    .appName("myApp") \
    .config("spark.mongodb.input.uri", "mongodb://10.7.40.54/eleicoes.candidatos2014") \
    .config("spark.mongodb.output.uri", "mongodb://10.7.40.54/eleicoes.candidatos2014") \
    .getOrCreate()

#conexão com a collection de resultados
spark_resultados = spark \
    .builder \
    .appName("myApp") \
    .config("spark.mongodb.input.uri", "mongodb://10.7.40.54/eleicoes.resultados2014") \
    .config("spark.mongodb.output.uri", "mongodb://10.7.40.54/eleicoes.resultados2014") \
    .getOrCreate()

#leitura dos dados dos candidatos
df_candidatos = spark_candidatos.read.format("com.mongodb.spark.sql.DefaultSource").load()
df_resultados = spark_resultados.read.format("com.mongodb.spark.sql.DefaultSource").load()

#filtragem dos candidatos eleitos
df_eleitos = df_resultados.filter(df_resultados['codigo_sit_cand_tot'] < 4).\
select('sq_candidato').\
distinct()

#seleciona informações úteis
df_informacoes = df_candidatos.select('sequencial_candidato', 'codigo_sexo', 'cod_grau_instrucao', 'codigo_cor_raca', 'despesa_max_campanha')

# Faz o join dos eleitos e das informações.
dados = df_eleitos.join(df_informacoes, df_eleitos['sq_candidato'] == df_informacoes['sequencial_candidato'], 'inner')

# Obtém as respostas desejadas (conta as entradas para cada coluna).
res_sexo = dados.groupby(['codigo_sexo']).count()
res_grau_instrucao = dados.groupby(['cod_grau_instrucao']).count()
res_cor = dados.groupby(['codigo_cor_raca']).count()
res_despesa = dados.groupby(['despesa_max_campanha']).count()

# Armazena o resultado no HDFS.
res_sexo.write.format("csv").save("hdfs://mcruz-master:9000/user/engdados/res_sexo.csv")
res_grau_instrucao.write.format("csv").save("hdfs://mcruz-master:9000/user/engdados/res_grau_instrucao.csv")
res_cor.write.format("csv").save("hdfs://mcruz-master:9000/user/engdados/res_cor")
res_despesa.write.format("csv").save("hdfs://mcruz-master:9000/user/engdados/res_despesa")

print 'Encerrado com sucesso.'


spark-submit --deploy-mode client --conf spark.cassandra.connection.host=10.7.40.94 --packages org.mongodb.spark:mongo-spark-connector_2.11:2.2.0 pergunta1.py
