from PIL import Image


def _bytes_to_bits(data: bytes):
    return [int(b) for byte in data for b in f"{byte:08b}"]


def _bits_to_bytes(bits):
    return bytes(int("".join(str(b) for b in bits[i:i+8]), 2) for i in range(0, len(bits), 8))


def embed_text_lsb(image_path: str, text: str, output_path: str):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    pixels = list(img.getdata())

    payload = text.encode("utf-8")
    length = len(payload)
    header = length.to_bytes(4, "big")
    data_bits = _bytes_to_bits(header + payload + b"\xff")

    capacity = w * h * 3
    if len(data_bits) > capacity:
        raise ValueError("Pesan terlalu panjang untuk gambar yang dipilih")

    out_pixels = []
    bit_i = 0
    for r, g, b in pixels:
        if bit_i < len(data_bits):
            r = (r & ~1) | data_bits[bit_i]
            bit_i += 1
        if bit_i < len(data_bits):
            g = (g & ~1) | data_bits[bit_i]
            bit_i += 1
        if bit_i < len(data_bits):
            b = (b & ~1) | data_bits[bit_i]
            bit_i += 1
        out_pixels.append((r, g, b))

    img_out = Image.new("RGB", (w, h))
    img_out.putdata(out_pixels)
    img_out.save(output_path)


def extract_text_lsb(image_path: str) -> str:
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    bits = []
    for r, g, b in pixels:
        bits.extend([r & 1, g & 1, b & 1])

    capacity = len(bits)
    header_bytes = _bits_to_bytes(bits[:32])
    length = int.from_bytes(header_bytes, "big")
    payload: bytes
    if 0 < length * 8 <= capacity - 32:
        payload_bits = bits[32:32 + length * 8]
        payload = _bits_to_bytes(payload_bits)
    else:
        cursor = 32
        buf = []
        while cursor + 8 <= capacity:
            byte_bits = bits[cursor:cursor + 8]
            b = int("".join(str(x) for x in byte_bits), 2)
            if b == 0xFF:
                break
            buf.append(b)
            cursor += 8
        payload = bytes(buf)
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload.decode("latin-1")


def analyze_text(text: str):
    data = text.encode("utf-8")
    rows = []
    for i, b in enumerate(data[:1024]):
        ch = chr(b) if 32 <= b <= 126 else "·"
        rows.append({"index": i, "dec": b, "hex": f"{b:02x}", "bin": f"{b:08b}", "char": ch})
    hex_lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hexstr = " ".join(f"{b:02x}" for b in chunk)
        ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        hex_lines.append(f"{i:08d}: {hexstr} | {ascii_str}")
    raw_view = " ".join(str(b) for b in data)
    return {
        "rows": rows,
        "hex_view": "\n".join(hex_lines),
        "raw_view": raw_view,
        "char_len": len(text),
        "byte_len": len(data),
    }


def embed_text_lsb_image(img: Image.Image, text: str) -> Image.Image:
    img = img.convert("RGB")
    w, h = img.size
    pixels = list(img.getdata())
    payload = text.encode("utf-8")
    length = len(payload)
    header = length.to_bytes(4, "big")
    data_bits = _bytes_to_bits(header + payload + b"\xff")
    capacity = w * h * 3
    if len(data_bits) > capacity:
        raise ValueError("Pesan terlalu panjang untuk gambar yang dipilih")
    out_pixels = []
    bit_i = 0
    for r, g, b in pixels:
        if bit_i < len(data_bits):
            r = (r & ~1) | data_bits[bit_i]
            bit_i += 1
        if bit_i < len(data_bits):
            g = (g & ~1) | data_bits[bit_i]
            bit_i += 1
        if bit_i < len(data_bits):
            b = (b & ~1) | data_bits[bit_i]
            bit_i += 1
        out_pixels.append((r, g, b))
    img_out = Image.new("RGB", (w, h))
    img_out.putdata(out_pixels)
    return img_out


def extract_text_lsb_image(img: Image.Image) -> str:
    img = img.convert("RGB")
    pixels = list(img.getdata())
    bits = []
    for r, g, b in pixels:
        bits.extend([r & 1, g & 1, b & 1])
    capacity = len(bits)
    header_bytes = _bits_to_bytes(bits[:32])
    length = int.from_bytes(header_bytes, "big")
    if 0 < length * 8 <= capacity - 32:
        payload_bits = bits[32:32 + length * 8]
        payload = _bits_to_bytes(payload_bits)
    else:
        cursor = 32
        buf = []
        while cursor + 8 <= capacity:
            byte_bits = bits[cursor:cursor + 8]
            b = int("".join(str(x) for x in byte_bits), 2)
            if b == 0xFF:
                break
            buf.append(b)
            cursor += 8
        payload = bytes(buf)
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload.decode("latin-1")
