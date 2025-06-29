ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    fill = SolidColor(Color(0xFF008000)),
  ) {
    moveTo(10f, 0f)
    lineTo(30f, 0f)
    arcTo(10f, 10f, 0f, false, true, 40f, 10f)
    lineTo(40f, 30f)
    arcTo(10f, 10f, 0f, false, true, 30f, 40f)
    lineTo(10f, 40f)
    arcTo(10f, 10f, 0f, false, true, 0f, 30f)
    lineTo(0f, 10f)
    arcTo(10f, 10f, 0f, false, true, 10f, 0f)
    close()
  }
}.build()