ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    fill = SolidColor(Color.Blue),
  ) {
    moveTo(10f, 10f)
    lineTo(60f, 10f)
    lineTo(60f, 40f)
    lineTo(10f, 40f)
    close()
  }
}.build()