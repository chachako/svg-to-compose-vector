ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 200.dp,
  defaultHeight = 100.dp,
  viewportWidth = 200f,
  viewportHeight = 100f,
).apply {
  path(
    fill = Brush.linearGradient(
      colorStops = arrayOf(
        0f to Color(0xFFFF6B35),
        0.5f to Color(0xFFF7931E),
        1f to Color(0xFFFFCC02)
      ),
      start = Offset(0f, 0f),
      end = Offset(100f, 0f)
    ),
  ) {
    moveTo(20f, 20f)
    lineTo(180f, 20f)
    lineTo(180f, 80f)
    lineTo(20f, 80f)
    close()
  }
}.build()