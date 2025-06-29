ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 200.dp,
  defaultHeight = 200.dp,
  viewportWidth = 200f,
  viewportHeight = 200f,
).apply {
  path(
    fill = SolidColor(Color(0xFF3498DB)),
    stroke = SolidColor(Color(0xFF2980B9)),
    strokeLineWidth = 2f,
  ) {
    moveTo(15f, 10f)
    lineTo(65f, 10f)
    arcTo(5f, 5f, 0f, false, true, 70f, 15f)
    lineTo(70f, 45f)
    arcTo(5f, 5f, 0f, false, true, 65f, 50f)
    lineTo(15f, 50f)
    arcTo(5f, 5f, 0f, false, true, 10f, 45f)
    lineTo(10f, 15f)
    arcTo(5f, 5f, 0f, false, true, 15f, 10f)
    close()
  }
  path(
    fill = SolidColor(Color(0xFFE74C3C)),
    stroke = SolidColor(Color(0xFFC0392B)),
    strokeLineWidth = 1f,
  ) {
    moveTo(130f, 30f)
    arcTo(20f, 20f, 0f, false, true, 150f, 10f)
    arcTo(20f, 20f, 0f, false, true, 170f, 30f)
    arcTo(20f, 20f, 0f, false, true, 150f, 50f)
    arcTo(20f, 20f, 0f, false, true, 130f, 30f)
    close()
  }
  path(
    fill = SolidColor(Color(0xFFF39C12)),
    stroke = SolidColor(Color(0xFFE67E22)),
    strokeLineWidth = 1.5f,
  ) {
    moveTo(20f, 100f)
    arcTo(30f, 20f, 0f, false, true, 50f, 80f)
    arcTo(30f, 20f, 0f, false, true, 80f, 100f)
    arcTo(30f, 20f, 0f, false, true, 50f, 120f)
    arcTo(30f, 20f, 0f, false, true, 20f, 100f)
    close()
  }
  path(
    fill = SolidColor(Color.Black),
    stroke = SolidColor(Color(0xFF9B59B6)),
    strokeLineWidth = 3f,
    strokeLineCap = StrokeCap.Round,
  ) {
    moveTo(120f, 80f)
    lineTo(180f, 120f)
  }
  path(
    fill = SolidColor(Color(0xFF2ECC71)),
    stroke = SolidColor(Color(0xFF27AE60)),
    strokeLineWidth = 2f,
  ) {
    moveTo(30f, 150f)
    lineTo(60f, 130f)
    lineTo(90f, 150f)
    lineTo(60f, 180f)
    close()
  }
  path(
    stroke = SolidColor(Color(0xFF34495E)),
    strokeLineWidth = 2f,
    strokeLineJoin = StrokeJoin.Round,
  ) {
    moveTo(120f, 150f)
    lineTo(140f, 140f)
    lineTo(160f, 160f)
    lineTo(180f, 150f)
  }
}.build()