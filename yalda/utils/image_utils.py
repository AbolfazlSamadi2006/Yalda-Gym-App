from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QPen, QColor
from PyQt6.QtCore import Qt, QRectF

def get_circular_pixmap(source_pixmap: QPixmap, size: int, border_color: str = "#8B0000", border_width: int = 3) -> QPixmap:
    """
    Center-crops a QPixmap into a square and clips it into a perfect anti-aliased circle,
    with an optional elegant dark red border ring.
    """
    if source_pixmap.isNull():
        return source_pixmap

    w, h = source_pixmap.width(), source_pixmap.height()
    min_dim = min(w, h)
    crop_rect = QRectF((w - min_dim) / 2, (h - min_dim) / 2, min_dim, min_dim)
    cropped = source_pixmap.copy(crop_rect.toRect())
    scaled = cropped.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)

    out = QPixmap(size, size)
    out.fill(Qt.GlobalColor.transparent)

    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, scaled)
    
    # Draw high quality anti-aliased border ring
    painter.setClipping(False)
    if border_width > 0 and border_color:
        pen = QPen(QColor(border_color))
        pen.setWidth(border_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        offset = border_width / 2.0
        painter.drawEllipse(QRectF(offset, offset, size - border_width, size - border_width))

    painter.end()

    return out
