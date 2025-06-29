ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    fill = SolidColor(Color.Black),
    stroke = SolidColor(Color(0xFF800080)),
    strokeLineWidth = 3f,
  ) {
    moveTo(0f, 0f)
    lineTo(50f, 50f)
  }
}.build()