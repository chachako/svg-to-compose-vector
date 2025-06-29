import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

val CustomIcon: ImageVector = ImageVector.Builder(
  name = "test_icon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    fill = SolidColor(Color(0xFF4285F4)),
  ) {
    moveTo(12f, 2f)
    lineTo(2f, 7f)
    verticalLineTo(17f)
    lineTo(12f, 22f)
    lineTo(22f, 17f)
    verticalLineTo(7f)
    lineTo(12f, 2f)
    close()
  }
}.build()