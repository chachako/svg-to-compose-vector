ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    stroke = SolidColor(Color(0xFF000080)),
    strokeLineWidth = 2f,
  ) {
    moveTo(5f, 5f)
    lineTo(25f, 25f)
    lineTo(45f, 5f)
    lineTo(45f, 45f)
  }
}.build()