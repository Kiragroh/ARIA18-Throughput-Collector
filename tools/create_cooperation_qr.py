"""Regenerate the public-project QR asset (optional build dependency: qrcode)."""
from pathlib import Path
import qrcode

PROJECT_URL = 'https://github.com/Kiragroh/ARIA18-Throughput-Collector'


def main():
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=4)
    qr.add_data(PROJECT_URL)
    qr.make(fit=True)
    path = Path(__file__).resolve().parents[1] / 'kooperation/assets/projekt-qr-code.png'
    qr.make_image(fill_color='black', back_color='white').save(path)
    print('PROJECT_QR_CREATED', PROJECT_URL)


if __name__ == '__main__':
    main()
