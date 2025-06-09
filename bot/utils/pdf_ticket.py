import io
import os
from datetime import datetime

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Регистрируем шрифт DejaVuSans
pdfmetrics.registerFont(TTFont("DejaVuSans", "bot/static/fonts/DejaVuSans.ttf"))


def generate_ticket_pdf(
    event_title: str,
    event_date: datetime,
    ticket_id: int,
    background_path: str | None = None,
) -> io.BytesIO:
    """Генерация PDF билета на основе декоративного шаблона A4 с обозначенными зонами"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # в pt (1pt = 1/72")

    # Рисуем фон-шаблон по всему листу
    if not background_path or not os.path.exists(background_path):
        background_path = os.path.join(
            "bot", "static", "images", "ticket_template_vintage.png"
        )
    if os.path.exists(background_path):
        bg = ImageReader(background_path)
        p.drawImage(bg, 0, 0, width=width, height=height)

    # Верхняя зона: название события
    # Плейсхолдер расположен с отступом 50pt от краёв, высота зоны ~120pt
    top_y = height - 50 - 60  # центр зоны вверх: от верхнего края 50pt, половина 120pt
    p.setFont("DejaVuSans", 24)
    p.drawCentredString(width / 2, top_y, event_title)

    # Нижняя левая зона: дата и номер
    detail_x = 50
    detail_y = 50
    detail_w = 330
    detail_h = 120
    p.setFont("DejaVuSans", 14)
    # Дата и время
    p.drawCentredString(
        detail_x + detail_w / 2,
        detail_y + detail_h - 20,
        f"Дата и время: {event_date.strftime('%d.%m.%Y %H:%M')}",
    )
    # Номер билета
    p.drawCentredString(
        detail_x + detail_w / 2, detail_y + 20, f"Номер билета: {ticket_id}"
    )

    # Нижняя правая зона: QR-код
    qr_size = 140
    qr = qrcode.make(f"TICKET:{ticket_id}")
    qr_buf = io.BytesIO()
    qr.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_img = ImageReader(qr_buf)
    qr_x = width - 50 - qr_size
    qr_y = 50
    p.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size)

    # Сохраняем PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
