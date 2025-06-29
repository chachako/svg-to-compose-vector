val StyleDemo: ImageVector = ImageVector.Builder(
  name = "style_test",
  defaultWidth = 100.0.dp,
  defaultHeight = 100.0.dp,
  viewportWidth = 100.0f,
  viewportHeight = 100.0f,
).apply {
  path(
    fill = Color(0xFFFF5722),
    stroke = Color(0xFF2196F3),
    fillAlpha = 0.6f,
    strokeAlpha = 0.8f,
    strokeLineWidth = 2.0f,
  ) {
    moveTo(10.0f, 10.0f)
    lineTo(50.0f, 10.0f)
    lineTo(50.0f, 30.0f)
    lineTo(10.0f, 30.0f)
    close()
  }
  path(
    fill = Color(0xFF4CAF50),
    stroke = Color(0xFFFF0000),
    strokeLineWidth = 3.0f,
  ) {
    moveTo(60.0f, 10.0f)
    lineTo(90.0f, 10.0f)
    lineTo(90.0f, 30.0f)
    lineTo(60.0f, 30.0f)
    close()
  }
  path(
    fill = Color(0xFFFFC107),
    stroke = Color(0xFFFF0000),
    strokeLineWidth = 1.5f,
    strokeLineCap = StrokeCap.Round,
    strokeLineJoin = StrokeJoin.Round,
  ) {
    moveTo(10.0f, 50.0f)
    lineTo(50.0f, 50.0f)
    lineTo(50.0f, 70.0f)
    lineTo(10.0f, 70.0f)
    close()
  }
}.build()