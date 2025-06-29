import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

ImageVector.Builder(
  name = "stroke_gradient_test",
  defaultWidth = 200f.dp,
  defaultHeight = 200f.dp,
  viewportWidth = 200f,
  viewportHeight = 200f,
).apply {
  path(
    stroke = Brush.linearGradient(
      colorStops = arrayOf(
        0f to Color.Red,
        0.5f to Color.Yellow,
        1f to Color.Blue
      ),
      start = Offset(0f, 0f),
      end = Offset(100f, 0f)
    ),
    strokeLineWidth = 6f,
  ) {
    moveTo(20f, 20f)
    lineTo(80f, 20f)
    lineTo(80f, 80f)
    lineTo(20f, 80f)
    close()
  }
  path(
    stroke = Brush.radialGradient(
      colorStops = arrayOf(0f to Color(0xFF800080), 1f to Color(0xFFFFA500)),
      center = Offset(50f, 50f),
      radius = 50f
    ),
    strokeLineWidth = 8f,
    strokeLineCap = StrokeCap.Round,
  ) {
    moveTo(150f, 50f)
    arcTo(30f, 30f, 0f, true, true, 149.99f, 50f)
  }
  path(
    fill = Brush.linearGradient(
      colorStops = arrayOf(0f to Color(0xB2ADD8E6), 1f to Color(0xB200008B)),
      start = Offset(0f, 0f),
      end = Offset(0f, 100f)
    ),
    stroke = Brush.linearGradient(
      colorStops = arrayOf(
        0f to Color.Red,
        0.5f to Color.Yellow,
        1f to Color.Blue
      ),
      start = Offset(0f, 0f),
      end = Offset(100f, 0f)
    ),
    strokeLineWidth = 4f,
    strokeLineJoin = StrokeJoin.Round,
  ) {
    moveTo(50f, 120f)
    lineTo(100f, 120f)
    lineTo(125f, 150f)
    lineTo(100f, 180f)
    lineTo(50f, 180f)
    lineTo(25f, 150f)
    close()
  }
  path(
    fill = SolidColor(Color.Black),
    stroke = Brush.radialGradient(
      colorStops = arrayOf(0f to Color(0xFF800080), 1f to Color(0xFFFFA500)),
      center = Offset(50f, 50f),
      radius = 50f
    ),
    strokeLineWidth = 12f,
    strokeLineCap = StrokeCap.Round,
  ) {
    moveTo(20f, 120f)
    lineTo(20f, 180f)
  }
  path(
    stroke = Brush.linearGradient(
      colorStops = arrayOf(
        0f to Color.Red,
        0.5f to Color.Yellow,
        1f to Color.Blue
      ),
      start = Offset(0f, 0f),
      end = Offset(100f, 0f)
    ),
    strokeLineWidth = 5f,
    strokeLineJoin = StrokeJoin.Round,
  ) {
    moveTo(140f, 120f)
    quadTo(170f, 140f, 140f, 160f)
    quadTo(110f, 140f, 140f, 120f)
  }
}.build()