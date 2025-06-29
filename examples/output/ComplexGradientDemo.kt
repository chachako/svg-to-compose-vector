ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 300.dp,
  defaultHeight = 150.dp,
  viewportWidth = 300f,
  viewportHeight = 150f,
).apply {
  path(
    fill = Brush.linearGradient(
      colorStops = arrayOf(
        0f to Color(0xFFE74C3C),
        0.25f to Color(0xCCF39C12),
        0.5f to Color(0x99F1C40F),
        0.75f to Color(0xCC27AE60),
        1f to Color(0xFF3498DB)
      ),
      start = Offset(0f, 0f),
      end = Offset(100f, 100f)
    ),
  ) {
    moveTo(50f, 25f)
    lineTo(250f, 25f)
    lineTo(275f, 75f)
    lineTo(250f, 125f)
    lineTo(50f, 125f)
    lineTo(25f, 75f)
    close()
  }
}.build()