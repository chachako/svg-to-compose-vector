ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    fill = SolidColor(Color(0xFFFFA500)),
  ) {
    moveTo(5f, 20f)
    arcTo(25f, 15f, 0f, false, true, 30f, 5f)
    arcTo(25f, 15f, 0f, false, true, 55f, 20f)
    arcTo(25f, 15f, 0f, false, true, 30f, 35f)
    arcTo(25f, 15f, 0f, false, true, 5f, 20f)
    close()
  }
}.build()