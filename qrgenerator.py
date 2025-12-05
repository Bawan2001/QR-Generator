"""
Modern QR Code Generator (PyQt6)
- Single-file app
- Requires: Python 3.8+
- pip install PyQt6 qrcode pillow

Features:
- Text / URL input
- Size and border controls
- Foreground/background color pickers
- Live preview
- Save as PNG
- Modern-styled UI (dark theme)

Run: python modern_qr_generator.py
"""

import sys
from io import BytesIO
from PIL import Image, ImageQt
import qrcode
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QColorDialog, QFileDialog,
    QSizePolicy, QCheckBox
)

class QRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Code Generator — Modern GUI")
        self.setMinimumSize(560, 420)
        self.setStyleSheet(self._style())
        self._build_ui()
        self.fg = "#000000"  # default black
        self.bg = "#ffffff"  # default white

    def _build_ui(self):
        root = QVBoxLayout(); root.setContentsMargins(18,18,18,18); root.setSpacing(12)

        # Input row
        row = QHBoxLayout()
        self.input = QLineEdit(); self.input.setPlaceholderText("Enter text or URL to encode...")
        self.input.returnPressed.connect(self.generate)
        btn = QPushButton("Generate")
        btn.clicked.connect(self.generate)
        row.addWidget(self.input); row.addWidget(btn)

        # Options row
        opts = QHBoxLayout(); opts.setSpacing(10)
        self.size_spin = QSpinBox(); self.size_spin.setRange(100, 1200); self.size_spin.setValue(300)
        self.size_spin.setSuffix(" px")
        self.border_spin = QSpinBox(); self.border_spin.setRange(0, 10); self.border_spin.setValue(4)
        self.color_fg = QPushButton("Foreground")
        self.color_fg.clicked.connect(self.pick_fg)
        self.color_bg = QPushButton("Background")
        self.color_bg.clicked.connect(self.pick_bg)
        self.save_btn = QPushButton("Save PNG")
        self.save_btn.clicked.connect(self.save_png)
        self.transparent_chk = QCheckBox("Transparent background")
        self.transparent_chk.stateChanged.connect(self._transparent_changed)

        opts.addWidget(QLabel("Size:")); opts.addWidget(self.size_spin)
        opts.addWidget(QLabel("Border:")); opts.addWidget(self.border_spin)
        opts.addWidget(self.color_fg); opts.addWidget(self.color_bg)
        opts.addWidget(self.transparent_chk); opts.addWidget(self.save_btn)

        # Preview
        self.preview = QLabel(); self.preview.setFixedSize(300,300); self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setObjectName("preview")

        # Footer / status
        self.status = QLabel("")
        self.status.setWordWrap(True)

        root.addLayout(row); root.addLayout(opts); root.addWidget(self.preview, alignment=Qt.AlignmentFlag.AlignCenter); root.addWidget(self.status)
        self.setLayout(root)

    def _transparent_changed(self, state):
        if state == Qt.CheckState.Checked:
            self.color_bg.setEnabled(False)
        else:
            self.color_bg.setEnabled(True)

    def pick_fg(self):
        c = QColorDialog.getColor(QColor(self.fg), parent=self, title="Select foreground color")
        if c.isValid():
            self.fg = c.name(); self.color_fg.setStyleSheet(f"background:{self.fg}; color: #fff;")

    def pick_bg(self):
        c = QColorDialog.getColor(QColor(self.bg), parent=self, title="Select background color")
        if c.isValid():
            self.bg = c.name(); self.color_bg.setStyleSheet(f"background:{self.bg}; color: #000;")

    def generate(self):
        text = self.input.text().strip()
        if not text:
            self.status.setText("Please enter text or a URL to encode.")
            return
        size = self.size_spin.value(); border = self.border_spin.value(); fill = self.fg; back = None if self.transparent_chk.isChecked() else self.bg
        try:
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=border)
            qr.add_data(text); qr.make(fit=True)
            img = qr.make_image(fill_color=fill, back_color=back).convert("RGBA")
            # resize to requested size keeping aspect
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            self._show_preview(img)
            self._last_image = img
            self.status.setText("QR generated — click Save PNG to export.")
        except Exception as e:
            self.status.setText(f"Error generating QR: {e}")

    def _show_preview(self, pil_img: Image.Image):
        qimg = ImageQt.ImageQt(pil_img)
        pix = QPixmap.fromImage(qimg)
        # scale down to preview widget
        pw = self.preview.width(); ph = self.preview.height()
        pix = pix.scaled(pw, ph, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.preview.setPixmap(pix)

    def save_png(self):
        if not hasattr(self, '_last_image'):
            self.status.setText("No QR image to save. Generate first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "qr.png", "PNG Files (*.png)")
        if not path:
            return
        try:
            # if transparent and bg is None, ensure alpha preserved
            self._last_image.save(path, format='PNG')
            self.status.setText(f"Saved: {path}")
        except Exception as e:
            self.status.setText(f"Failed to save: {e}")

    def _style(self):
        return """
        QWidget { background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #0f172a, stop:1 #020617); color: #e6edf3; font-family: 'Segoe UI'; }
        QLineEdit { background: rgba(255,255,255,0.04); border-radius: 8px; padding: 8px; }
        QPushButton { background: qlineargradient(x1:0 y1:0, x2:1 y2:0, stop:0 #06b6d4, stop:1 #3b82f6); border-radius: 8px; padding: 8px 12px; color: white; }
        QPushButton:hover { opacity: 0.9 }
        #preview { background: rgba(255,255,255,0.02); border-radius: 8px; }
        QLabel { color: #e6edf3 }
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QRApp(); w.show(); sys.exit(app.exec())
