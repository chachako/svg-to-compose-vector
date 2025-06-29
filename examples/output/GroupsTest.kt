ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  group(
    name = "base-layer",
    translationX = 2f,
    translationY = 2f,
  ) {
    group(
      name = "background",
      scaleX = 0.9f,
      scaleY = 0.9f,
    ) {
      path(
        fill = SolidColor(Color(0xFFE0E0E0)),
        stroke = SolidColor(Color(0xFFBDBDBD)),
        strokeLineWidth = 1f,
      ) {
        moveTo(10f, 0f)
        arcTo(10f, 10f, 0f, true, true, -10f, 0f)
        arcTo(10f, 10f, 0f, true, true, 10f, 0f)
        close()
      }
    }
    group(
      name = "foreground",
      rotate = 45f,
      translationX = 5f,
      translationY = 5f,
    ) {
      path(
        fill = SolidColor(Color(0xFF2196F3)),
      ) {
        moveTo(-2f, -2f)
        lineTo(2f, -2f)
        lineTo(2f, 2f)
        lineTo(-2f, 2f)
        close()
      }
      group(
        name = "accents",
        scaleX = 0.5f,
        scaleY = 0.5f,
      ) {
        path(
          fill = SolidColor(Color(0xFFFF5722)),
        ) {
          moveTo(-6f, -6f)
          lineTo(-4f, -6f)
          lineTo(-4f, -4f)
          lineTo(-6f, -4f)
          close()
        }
        path(
          fill = SolidColor(Color(0xFFFF5722)),
        ) {
          moveTo(4f, -6f)
          lineTo(6f, -6f)
          lineTo(6f, -4f)
          lineTo(4f, -4f)
          close()
        }
        path(
          fill = SolidColor(Color(0xFFFF5722)),
        ) {
          moveTo(4f, 4f)
          lineTo(6f, 4f)
          lineTo(6f, 6f)
          lineTo(4f, 6f)
          close()
        }
        path(
          fill = SolidColor(Color(0xFFFF5722)),
        ) {
          moveTo(-6f, 4f)
          lineTo(-4f, 4f)
          lineTo(-4f, 6f)
          lineTo(-6f, 6f)
          close()
        }
      }
    }
  }
}.build()