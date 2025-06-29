ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24.0.dp,
  defaultHeight = 24.0.dp,
  viewportWidth = 24.0f,
  viewportHeight = 24.0f,
).apply {
  group(
    translationX = 2.0f,
    translationY = 2.0f,
  ) {
    group(
      scaleX = 0.9f,
      scaleY = 0.9f,
    ) {
      path(
        fill = Color(0xFFE0E0E0),
        stroke = Color(0xFFBDBDBD),
        strokeLineWidth = 1.0f,
      ) {
        moveTo(10.0f, 0.0f)
        arcTo(10.0f, 10.0f, 0.0f, true, true, -10.0f, 0.0f)
        arcTo(10.0f, 10.0f, 0.0f, true, true, 10.0f, 0.0f)
        close()
      }
    }
    group(
      rotate = 44.99999999999999f,
      translationX = 5.0f,
      translationY = 5.0f,
    ) {
      path(
        fill = Color(0xFF2196F3),
      ) {
        moveTo(-2.0f, -2.0f)
        lineTo(2.0f, -2.0f)
        lineTo(2.0f, 2.0f)
        lineTo(-2.0f, 2.0f)
        close()
      }
      group(
        scaleX = 0.5f,
        scaleY = 0.5f,
      ) {
        path(
          fill = Color(0xFFFF5722),
        ) {
          moveTo(-6.0f, -6.0f)
          lineTo(-4.0f, -6.0f)
          lineTo(-4.0f, -4.0f)
          lineTo(-6.0f, -4.0f)
          close()
        }
        path(
          fill = Color(0xFFFF5722),
        ) {
          moveTo(4.0f, -6.0f)
          lineTo(6.0f, -6.0f)
          lineTo(6.0f, -4.0f)
          lineTo(4.0f, -4.0f)
          close()
        }
        path(
          fill = Color(0xFFFF5722),
        ) {
          moveTo(4.0f, 4.0f)
          lineTo(6.0f, 4.0f)
          lineTo(6.0f, 6.0f)
          lineTo(4.0f, 6.0f)
          close()
        }
        path(
          fill = Color(0xFFFF5722),
        ) {
          moveTo(-6.0f, 4.0f)
          lineTo(-4.0f, 4.0f)
          lineTo(-4.0f, 6.0f)
          lineTo(-6.0f, 6.0f)
          close()
        }
      }
    }
  }
}.build()