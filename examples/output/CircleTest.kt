ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    fill = SolidColor(Color.Red),
  ) {
    moveTo(5f, 25f)
    arcTo(20f, 20f, 0f, false, true, 25f, 5f)
    arcTo(20f, 20f, 0f, false, true, 45f, 25f)
    arcTo(20f, 20f, 0f, false, true, 25f, 45f)
    arcTo(20f, 20f, 0f, false, true, 5f, 25f)
    close()
  }
}.build()