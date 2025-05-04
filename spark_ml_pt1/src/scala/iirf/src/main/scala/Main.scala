import org.apache.spark.sql.api.java.UDF1

class iirFilter extends UDF1[Seq[Double], Seq[Double]] {

  override def call(x: Seq[Double]): Seq[Double] = {

    val alpha = 0.7

    val output = new Array[Double](x.length)
    for (i <- x.indices) {
      if (i == 0) output(i) = x(i)
      else output(i) = (1 - alpha) * x(i) + alpha * output(i - 1)
    }
    output.toSeq
  }
}