ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 120f.dp,
  defaultHeight = 120f.dp,
  viewportWidth = 120f,
  viewportHeight = 120f,
).apply {
  path(
    fill = Brush.radialGradient(
      colorStops = arrayOf(
        0f to Color(0xFFFFFFFF),
        0.7f to Color(0xE587CEEB),
        1f to Color(0xCC191970)
      ),
      center = Offset(50f, 30f),
      radius = 60f
    ),
  ) {
    moveTo(110f, 60f)
    arcTo(50f, 50f, 0f, true, true, 10f, 60f)
    arcTo(50f, 50f, 0f, true, true, 110f, 60f)
    close()
  }
}.build()