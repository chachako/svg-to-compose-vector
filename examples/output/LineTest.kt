ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
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