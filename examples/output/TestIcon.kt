val TestIcon: ImageVector = ImageVector.Builder(
  name = "test_icon",
  defaultWidth = 24.0.dp,
  defaultHeight = 24.0.dp,
  viewportWidth = 24.0f,
  viewportHeight = 24.0f,
).apply {
  path(
    fill = Color(0xFF4285F4),
  ) {
    moveTo(12.0f, 2.0f)
    lineTo(2.0f, 7.0f)
    verticalLineTo(17.0f)
    lineTo(12.0f, 22.0f)
    lineTo(22.0f, 17.0f)
    verticalLineTo(7.0f)
    lineTo(12.0f, 2.0f)
    close()
  }
}.build()