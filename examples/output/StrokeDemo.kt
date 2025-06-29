val StrokeDemo: ImageVector = ImageVector.Builder(
  name = "stroke_test",
  defaultWidth = 100.0.dp,
  defaultHeight = 100.0.dp,
  viewportWidth = 100.0f,
  viewportHeight = 100.0f,
).apply {
  path(
    stroke = Color(0xFF2196F3),
    strokeLineWidth = 3.0f,
    strokeLineCap = StrokeCap.Round,
  ) {
    moveTo(50.0f, 25.0f)
    arcTo(15.0f, 15.0f, 0.0f, true, true, 49.99f, 25.0f)
  }
  path(
    fill = Color(0xFFFFEB3B),
    stroke = Color(0xFFFF0000),
    fillAlpha = 0.6f,
    strokeAlpha = 0.8f,
    strokeLineWidth = 2.0f,
  ) {
    moveTo(20.0f, 60.0f)
    lineTo(50.0f, 60.0f)
    lineTo(50.0f, 80.0f)
    lineTo(20.0f, 80.0f)
    close()
  }
  path(
    stroke = Color(0xFF00FF00),
    strokeLineWidth = 4.0f,
    strokeLineCap = StrokeCap.Round,
    strokeLineJoin = StrokeJoin.Round,
  ) {
    moveTo(60.0f, 60.0f)
    lineTo(75.0f, 70.0f)
    lineTo(90.0f, 60.0f)
  }
}.build()