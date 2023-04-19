import qrcode


def generate_qr_code(medical_data, key):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(f'{medical_data}|{key}')
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save('qr_code.png')
