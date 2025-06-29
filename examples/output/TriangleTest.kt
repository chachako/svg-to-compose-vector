ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    fill = SolidColor(Color.Yellow),
  ) {
    moveTo(25f, 5f)
    lineTo(45f, 40f)
    lineTo(5f, 40f)
    close()
  }
}.build()