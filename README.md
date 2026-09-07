SA-Civic-Pulse/
├── venv/                       # virtual environment (gitignored)
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── Makefile                    # your addition — run_docker_test_db target
├── gdelt_example.py             # exploration script from Day 1
├── masterfilelist.txt           # gitignored, too large to commit
├── pipeline/
│   ├── schema.sql               # DONE — 4 tables: event_time, event_location, event_action_type, event_fact
│   ├── extract.py                # NOT built yet — today, Day 3
│   ├── transform_spark.py        # NOT built yet — Day 5-6
│   └── load.py                    # NOT built yet — Day 7
├── api/
│   └── main.py                    # NOT built yet — Day 9
├── tests/                          # empty
├── docs/                            # empty — diagrams/README come Day 9-10


check out: some results in transform finds south africa in context, not geo country,
SF is then followed by a number that represents the resolution ie: 1=country, 4=city, 5=state/province

-------------------------------------------------------------------------------------------------------------------------

WARNING: Using incubator modules: jdk.incubator.vector
Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
26/09/05 19:51:08 WARN Utils: Your hostname, BeanMachine, resolves to a loopback address: 127.0.1.1; using 192.168.10.196 instead (on interface wlan0)
26/09/05 19:51:08 WARN Utils: Set SPARK_LOCAL_IP if you need to bind to another address
Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
/home/zuzubean/Projects/SA-Civic-Pulse/venv/lib/python3.14/site-packages/pyspark/testing/utils.py:127: FutureWarning: PySpark does not yet fully support pandas >= 3.0.0. Some features may not work correctly. It is recommended to use pandas < 3.0.0 for now.
  require_minimum_pandas_version()
26/09/05 19:51:09 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
26/09/05 19:51:12 WARN FileStreamSink: Assume no metadata directory. Error while looking for metadata directory in the path: data/raw/*.export.CSV.
java.io.FileNotFoundException: File data/raw/*.export.CSV does not exist
        at org.apache.hadoop.fs.RawLocalFileSystem.deprecatedGetFileStatus(RawLocalFileSystem.java:980)
        at org.apache.hadoop.fs.RawLocalFileSystem.getFileLinkStatusInternal(RawLocalFileSystem.java:1301)
        at org.apache.hadoop.fs.RawLocalFileSystem.getFileStatus(RawLocalFileSystem.java:970)
        at org.apache.hadoop.fs.FilterFileSystem.getFileStatus(FilterFileSystem.java:462)
        at org.apache.spark.sql.execution.streaming.sinks.FileStreamSink$.hasMetadata(FileStreamSink.scala:58)
        at org.apache.spark.sql.execution.datasources.DataSource.resolveRelation(DataSource.scala:394)
        at org.apache.spark.sql.catalyst.analysis.ResolveDataSource.org$apache$spark$sql$catalyst$analysis$ResolveDataSource$$loadV1BatchSource(ResolveDataSource.scala:210)
        at org.apache.spark.sql.catalyst.analysis.ResolveDataSource$$anonfun$apply$1.$anonfun$applyOrElse$2(ResolveDataSource.scala:62)
        at scala.Option.getOrElse(Option.scala:201)
        at org.apache.spark.sql.catalyst.analysis.ResolveDataSource$$anonfun$apply$1.applyOrElse(ResolveDataSource.scala:62)
        at org.apache.spark.sql.catalyst.analysis.ResolveDataSource$$anonfun$apply$1.applyOrElse(ResolveDataSource.scala:46)
        at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.$anonfun$resolveOperatorsUpWithPruning$3(AnalysisHelper.scala:139)
        at org.apache.spark.sql.catalyst.trees.CurrentOrigin$.withOrigin(origin.scala:107)
        at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.$anonfun$resolveOperatorsUpWithPruning$1(AnalysisHelper.scala:139)
        at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper$.allowInvokingTransformsInAnalyzer(AnalysisHelper.scala:416)
        at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.resolveOperatorsUpWithPruning(AnalysisHelper.scala:135)
        at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.resolveOperatorsUpWithPruning$(AnalysisHelper.scala:131)
        at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.resolveOperatorsUpWithPruning(LogicalPlan.scala:37)
        at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.resolveOperatorsUp(AnalysisHelper.scala:112)
        at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper.resolveOperatorsUp$(AnalysisHelper.scala:111)
        at org.apache.spark.sql.catalyst.plans.logical.LogicalPlan.resolveOperatorsUp(LogicalPlan.scala:37)
        at org.apache.spark.sql.catalyst.analysis.ResolveDataSource.apply(ResolveDataSource.scala:46)
        at org.apache.spark.sql.catalyst.analysis.ResolveDataSource.apply(ResolveDataSource.scala:44)
        at org.apache.spark.sql.catalyst.rules.RuleExecutor.$anonfun$execute$2(RuleExecutor.scala:248)
        at scala.collection.LinearSeqOps.foldLeft(LinearSeq.scala:183)
        at scala.collection.LinearSeqOps.foldLeft$(LinearSeq.scala:179)
        at scala.collection.immutable.List.foldLeft(List.scala:79)
        at org.apache.spark.sql.catalyst.rules.RuleExecutor.$anonfun$execute$1(RuleExecutor.scala:245)
        at org.apache.spark.sql.catalyst.rules.RuleExecutor.$anonfun$execute$1$adapted(RuleExecutor.scala:237)
        at scala.collection.immutable.List.foreach(List.scala:323)
        at org.apache.spark.sql.catalyst.rules.RuleExecutor.execute(RuleExecutor.scala:237)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.super$execute(Analyzer.scala:438)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.$anonfun$executeSameContext$1(Analyzer.scala:438)
        at org.apache.spark.sql.internal.SQLConf$.withExistingConf(SQLConf.scala:171)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.runWithSessionConf(Analyzer.scala:400)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.org$apache$spark$sql$catalyst$analysis$Analyzer$$executeSameContext(Analyzer.scala:438)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.$anonfun$execute$1(Analyzer.scala:433)
        at org.apache.spark.sql.catalyst.analysis.AnalysisContext$.withNewAnalysisContext(Analyzer.scala:276)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.execute(Analyzer.scala:433)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.execute(Analyzer.scala:336)
        at org.apache.spark.sql.catalyst.rules.RuleExecutor.$anonfun$executeAndTrack$1(RuleExecutor.scala:207)
        at org.apache.spark.sql.catalyst.QueryPlanningTracker$.withTracker(QueryPlanningTracker.scala:89)
        at org.apache.spark.sql.catalyst.rules.RuleExecutor.executeAndTrack(RuleExecutor.scala:207)
        at org.apache.spark.sql.catalyst.analysis.resolver.HybridAnalyzer.resolveInFixedPoint(HybridAnalyzer.scala:273)
        at org.apache.spark.sql.catalyst.analysis.resolver.HybridAnalyzer.$anonfun$apply$1(HybridAnalyzer.scala:82)
        at org.apache.spark.sql.catalyst.analysis.resolver.HybridAnalyzer.withTrackedAnalyzerBridgeState(HybridAnalyzer.scala:117)
        at org.apache.spark.sql.catalyst.analysis.resolver.HybridAnalyzer.apply(HybridAnalyzer.scala:75)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.runAnalysis$1(Analyzer.scala:368)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.$anonfun$executeAndCheck$2(Analyzer.scala:373)
        at org.apache.spark.sql.internal.SQLConf$.withExistingConf(SQLConf.scala:171)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.runWithSessionConf(Analyzer.scala:400)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.$anonfun$executeAndCheck$1(Analyzer.scala:373)
        at org.apache.spark.sql.catalyst.plans.logical.AnalysisHelper$.markInAnalyzer(AnalysisHelper.scala:423)
        at org.apache.spark.sql.catalyst.analysis.Analyzer.executeAndCheck(Analyzer.scala:373)
        at org.apache.spark.sql.execution.QueryExecution.$anonfun$lazyAnalyzed$2(QueryExecution.scala:200)
        at org.apache.spark.sql.catalyst.QueryPlanningTracker.measurePhase(QueryPlanningTracker.scala:148)
        at org.apache.spark.sql.execution.QueryExecution.$anonfun$executePhase$3(QueryExecution.scala:410)
        at org.apache.spark.sql.execution.QueryExecution.withQueryExecutionId(QueryExecution.scala:429)
        at org.apache.spark.sql.execution.QueryExecution.$anonfun$executePhase$2(QueryExecution.scala:410)
        at org.apache.spark.sql.execution.QueryExecution$.withInternalError(QueryExecution.scala:872)
        at org.apache.spark.sql.execution.QueryExecution.$anonfun$executePhase$1(QueryExecution.scala:409)
        at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:810)
        at org.apache.spark.sql.execution.QueryExecution.executePhase(QueryExecution.scala:408)
        at org.apache.spark.sql.execution.QueryExecution.$anonfun$lazyAnalyzed$1(QueryExecution.scala:200)
        at scala.util.Try$.apply(Try.scala:217)
        at org.apache.spark.util.Utils$.doTryWithCallerStacktrace(Utils.scala:1407)
        at org.apache.spark.util.LazyTry.tryT$lzycompute(LazyTry.scala:46)
        at org.apache.spark.util.LazyTry.tryT(LazyTry.scala:46)
        at org.apache.spark.util.LazyTry.get(LazyTry.scala:61)
        at org.apache.spark.sql.execution.QueryExecution.$anonfun$analyzed$1(QueryExecution.scala:212)
        at org.apache.spark.sql.execution.QueryExecution.withAbortTransactionOnFailure(QueryExecution.scala:632)
        at org.apache.spark.sql.execution.QueryExecution.analyzed(QueryExecution.scala:212)
        at org.apache.spark.sql.execution.QueryExecution.assertAnalyzed(QueryExecution.scala:151)
        at org.apache.spark.sql.classic.Dataset$.$anonfun$ofRows$1(Dataset.scala:114)
        at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:810)
        at org.apache.spark.sql.classic.Dataset$.ofRows(Dataset.scala:112)
        at org.apache.spark.sql.classic.DataFrameReader.load(DataFrameReader.scala:109)
        at org.apache.spark.sql.classic.DataFrameReader.load(DataFrameReader.scala:58)
        at org.apache.spark.sql.DataFrameReader.csv(DataFrameReader.scala:392)
        at org.apache.spark.sql.classic.DataFrameReader.csv(DataFrameReader.scala:259)
        at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103)
        at java.base/java.lang.reflect.Method.invoke(Method.java:580)
        at py4j.reflection.MethodInvoker.invoke(MethodInvoker.java:244)
        at py4j.reflection.ReflectionEngine.invoke(ReflectionEngine.java:374)
        at py4j.Gateway.invoke(Gateway.java:282)
        at py4j.commands.AbstractCommand.invokeMethod(AbstractCommand.java:132)
        at py4j.commands.CallCommand.execute(CallCommand.java:79)
        at py4j.ClientServerConnection.waitForCommands(ClientServerConnection.java:184)
        at py4j.ClientServerConnection.run(ClientServerConnection.java:108)
        at java.base/java.lang.Thread.run(Thread.java:1583)
Loaded 738763 total rows from all raw files.                                    
Filtered down to 6333 South African rows (0.86% of total).                      

Geocoding granularity breakdown (ActionGeo_Type):
+--------------+-----+                                                          
|ActionGeo_Type|count|
+--------------+-----+
|             1| 1280|
|             4| 4684|
|             5|  369|
+--------------+-----+


Sample of cleaned data:
+---------------+----------+----+-----+-------+---------------+---------+--------------------+---------------+---------------+----------+--------------------------------+-----------+--------------+-----------+--------------+---------------
|global_event_id|sql_date  |year|month|quarter|action_geo_type|adm1_code|action_geo_full_name|cameo_root_code|cameo_base_code|quad_class|category_label                  |actor1_name|actor1_country|actor2_name|actor2_country|goldstein_scale|avg_tone  |num_mentions|num_sources|num_articles|source_url                                                                                                         |date_added         |
+---------------+----------+----+-----+-------+---------------+---------+--------------------+---------------+---------------+----------+--------------------------------+-----------+--------------+-----------+--------------+---------------
|1261181205     |2025-09-04|2025|9    |3      |1              |SF       |South Africa        |01             |012            |1         |Make Public Statement           |NULL       |NULL          |SCHOOL     |NULL          |-0.4           |-2.3284998|5           |1          |5           |https://www.psychiatrictimes.com/view/the-august-2025-special-report-diversity                                     |2025-09-04 00:00:00|
|1261181225     |2025-09-04|2025|9    |3      |1              |SF       |South Africa        |05             |051            |1         |Engage in Diplomatic Cooperation|NULL       |NULL          |SCHOOL     |NULL          |3.4            |-2.3284998|5           |1          |5           |https://www.psychiatrictimes.com/view/the-august-2025-special-report-diversity                                     |2025-09-04 00:00:00|
|1261182173     |2025-09-04|2025|9    |3      |1              |SF       |South Africa        |02             |020            |1         |Appeal                          |STUDENT    |NULL          |NULL       |NULL          |3.0            |3.164557  |10          |1          |10          |https://www.opportunitiesforafricans.com/absa-fellowship-programme-2026-for-undergraduates-studies-in-south-africa/|2025-09-04 00:00:00|
|1261182177     |2025-09-04|2025|9    |3      |1              |SF       |South Africa        |03             |036            |1         |Express Intent to Cooperate     |STUDENT    |NULL          |NULL       |NULL          |4.0            |3.164557  |5           |1          |5           |https://www.opportunitiesforafricans.com/absa-fellowship-programme-2026-for-undergraduates-studies-in-south-africa/|2025-09-04 00:00:00|
|1261070992     |2025-09-03|2025|9    |3      |1              |SF       |South Africa        |03             |036            |1         |Express Intent to Cooperate     |WEST BANK  |PSE           |NULL       |NULL          |4.0            |-4.716981 |4           |1          |4           |https://www.globalsecurity.org/military/library/news/2025/09/mil-250902-presstv09.htm                              |2025-09-03 12:30:00|
+---------------+----------+----+-----+-------+---------------+---------+--------------------+---------------+---------------+----------+--------------------------------+-----------+--------------+-----------+--------------+---------------
only showing top 5 rows
26/09/05 19:51:24 WARN MemoryManager: Total allocation exceeds 95,00% (1 020 054 720 bytes) of heap memory
Scaling row group sizes to 95,00% for 8 writers
26/09/05 19:51:26 WARN MemoryManager: Total allocation exceeds 95,00% (1 020 054 720 bytes) of heap memory
Scaling row group sizes to 95,00% for 8 writers
                                                                                
Wrote cleaned data to data/processed/events