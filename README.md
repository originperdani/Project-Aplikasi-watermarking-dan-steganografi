# Mini Aplikasi Pengolahan Citra Digital — Watermarking & Steganografi

Aplikasi web sederhana untuk menambahkan watermark pada gambar dan melakukan steganografi (menyisipkan serta mengekstrak pesan rahasia dari gambar) dengan metode LSB. Dibangun menggunakan Flask dan Pillow.

## Ringkasan Fitur

- Watermark teks: atur posisi, ukuran, warna, margin, dan opacity.
- Watermark gambar (logo): atur skala, posisi, margin, dan opacity.
- Steganografi LSB: sembunyikan pesan teks ke dalam gambar dan ekstrak kembali.
- Tampilan analisis hasil ekstraksi: teks, hex view, dan raw bytes.

## Arsitektur Singkat

- Backend: Flask (`app.py`) dengan route utama `"/"`, `"/watermark"`, `"/steg"`, dan penyajian hasil di `"/outputs/<filename>"`.
- Template: HTML di `templates/` (`index.html`, `watermark.html`, `steg.html`).
- Utilitas:
  - `utils/watermark.py`: fungsi `add_text_watermark(...)` dan `add_image_watermark(...)` untuk watermark.
  - `utils/steg.py`: fungsi `embed_text_lsb(...)`, `extract_text_lsb(...)`, dan `analyze_text(...)` untuk steganografi.
- Static: gaya CSS di `static/styles.css`.
- I/O: unggahan masuk ke `uploads/`, hasil diproduksi ke `outputs/`.

## Persyaratan

- Python 3.10+ disarankan
- Paket Python:
  - Flask
  - Pillow

Instalasi cepat:

```bash
pip install flask pillow
```

Opsional (disarankan): gunakan virtual environment.

## Menjalankan Aplikasi

```bash
python app.py
```

Lalu buka `http://127.0.0.1:8000/` di browser.

Secara default aplikasi berjalan dengan `debug=True` pada port `8000`.

## Cara Penggunaan

### 1) Watermark

Menu: `Beranda → Watermark`

- Unggah `Gambar` sumber (format: PNG/JPG/JPEG/BMP).
- Pilih `Mode`:
  - `Teks`: isi `Teks`, atur `Ukuran Font`, pilih `Warna`.
  - `Gambar`: unggah `Gambar Watermark` (logo), atur `Skala`.
- Atur `Posisi` (atas/bawah kiri/kanan, tengah), `Margin`, dan `Opacity`.
- Klik `Proses` untuk menghasilkan gambar ber-watermark.
- Hasil tampil di halaman, dapat diunduh via tombol `Unduh`.

Catatan:

- Watermark teks memakai font `arial.ttf` jika tersedia; bila tidak, fallback ke font default.
- Output disimpan sebagai file baru di folder `outputs/`.

### 2) Steganografi

Menu: `Beranda → Steganografi`

Terdapat dua tab: `Sembunyikan` (embed) dan `Ekstrak`.

Embed (Sembunyikan):

- Unggah gambar sumber (disarankan PNG/BMP untuk menghindari hilangnya bit akibat kompresi lossy).
- Masukkan `Pesan` yang ingin disisipkan.
- Perhatikan indikator kapasitas maksimum karakter berdasarkan ukuran gambar.
- Klik `Sembunyikan` untuk menghasilkan gambar stego (output `.png`).
- Hasil dapat diunduh dan dipreview.

Ekstrak:

- Unggah gambar stego.
- Klik `Ekstrak` untuk mendapatkan pesan.
- Lihat hasil dalam tiga tampilan: `Teks`, `Hex View`, dan `Raw View` (tabel byte per karakter).

## Alur Internal (Ringkas)

- Watermark (`/watermark`):

  - Validasi file dan format, simpan ke `uploads/`.
  - Mode teks: render overlay teks dengan `opacity` dan posisi yang dipilih.
  - Mode gambar: ubah ukuran logo berdasar `scale`, terapkan `opacity`, tempel di posisi yang dipilih.
  - Simpan hasil ke `outputs/`, tampilkan link unduh.

- Steganografi (`/steg`):
  - Embed: hitung kapasitas `w*h*3` bit, siapkan header panjang (4 byte big‑endian) + payload UTF‑8 + sentinel `0xFF`, tulis ke LSB kanal RGB secara berurutan. Simpan hasil sebagai PNG.
  - Ekstrak: baca kembali LSB; jika header valid, gunakan panjang; bila tidak, jatuhkan ke pembacaan hingga sentinel. Decode ke UTF‑8 (fallback Latin‑1 bila perlu). Tampilkan analisis byte.

## Format yang Didukung

- Gambar: `PNG`, `JPG/JPEG`, `BMP`. Untuk steganografi, `PNG/BMP` lebih aman karena non‑lossy.

## Struktur Direktori

```
Project Aplikasi Mini watermarking dan steganografi/
├─ app.py
├─ static/
│  └─ styles.css
├─ templates/
│  ├─ index.html
│  ├─ watermark.html
│  └─ steg.html
├─ uploads/        # file yang diunggah pengguna
├─ outputs/        # file hasil proses (dibuat otomatis saat runtime)
└─ utils/
   ├─ watermark.py
   └─ steg.py
```

## Tips & Rekomendasi

- Steganografi: gunakan gambar dengan resolusi cukup agar kapasitas pesan memadai; hindari JPG bila ingin menjaga integritas bit.
- Watermark: gunakan `opacity` moderat agar watermark tetap terlihat tanpa mengganggu konten utama.
- Keamanan: aplikasi ini untuk tujuan edukasi; jangan gunakan untuk menyimpan data sensitif tanpa pengamanan tambahan.

## Troubleshooting

- "Format gambar tidak didukung": pastikan ekstensi termasuk `png`, `jpg`, `jpeg`, atau `bmp`.
- "Pesan terlalu panjang": kurangi panjang pesan atau gunakan gambar berukuran lebih besar.
- Font `arial.ttf` tidak ditemukan: sistem akan memakai font default; ukuran visual bisa sedikit berbeda.
