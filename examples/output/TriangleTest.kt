ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
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