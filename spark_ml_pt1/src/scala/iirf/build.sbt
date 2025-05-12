val scala3Version = "2.12.19"

lazy val root = project
  .in(file("."))
  .settings(
    name := "iirf",
    version := "0.1.0-SNAPSHOT",

    scalaVersion := scala3Version,

    libraryDependencies += "org.scalameta" %% "munit" % "1.0.0" % Test,
    libraryDependencies += "org.apache.spark" %% "spark-sql" % "3.2.0" % "provided"
  )