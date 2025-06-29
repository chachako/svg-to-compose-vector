val AdvancedPaths: ImageVector = ImageVector.Builder(
  name = "advanced_test",
  defaultWidth = 100.0.dp,
  defaultHeight = 100.0.dp,
  viewportWidth = 100.0f,
  viewportHeight = 100.0f,
).apply {
  path(
    fill = Color(0xFFFF6B35),
  ) {
    moveTo(20.0f, 20.0f)
    quadTo(50.0f, 10.0f, 80.0f, 20.0f)
    reflectiveQuadTo(80.0f, 50.0f)
    reflectiveCurveTo(70.0f, 80.0f, 50.0f, 80.0f)
    arcTo(10.0f, 10.0f, 0.0f, false, true, 20.0f, 70.0f)
    close()
  }
}.build()