# Shuttle Kampus — UTS Web Application Development (Individu)

Aplikasi pencatat jadwal shuttle kampus. Backend **FastAPI** + frontend **Vue 3 (Vite)**, dataset in-memory buatan sendiri (12 baris sintetis di `backend/app/data.py`).

## Cara menjalankan

### Backend (port 8000)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Dokumentasi interaktif: http://localhost:8000/docs

### Frontend (port 5173)
```bash
cd frontend
npm install
npm run dev
```
Buka http://localhost:5173. Alamat API bisa diubah lewat env `VITE_API_URL` (default `http://localhost:8000`).

## Verifikasi requirement

| Requirement | Cara verifikasi |
|---|---|
| Dataset in-memory ≥ 12 baris | Buka `backend/app/data.py`; atau `GET /sessions?page_size=50` → `total` = 12 |
| `GET /sessions` + pagination + search | `/sessions?page=2&page_size=5`; `/sessions?search=asrama` (cari di rute & sopir) |
| `GET /sessions/{id}` + 404 | `/sessions/1` → 200; `/sessions/999` → 404 |
| `POST /sessions` (Pydantic, 201) | Di `/docs` kirim data valid → 201; jam `25:99` atau `booked > capacity` → 422 |
| `DELETE /sessions/{id}` (204) | Hapus id yang ada → 204; ulangi → 404 |
| CORS | Frontend di `localhost:5173` bisa memanggil API tanpa error CORS di console |
| Frontend: empat state + retry | Loading saat fetch; matikan backend → pesan error + tombol **Coba lagi**; cari kata ngawur → state kosong; normal → tabel |
| Form create + validasi | Kirim form kosong → pesan error per field (validasi klien); error dari server ditampilkan juga |
| Hapus dengan konfirmasi | Klik **Hapus** → dialog konfirmasi; batal = tidak terhapus |

## Catatan desain
- Data disimpan di memori: restart server mengembalikan data ke kondisi awal.
- Validasi ada di dua sisi: klien (UX cepat) dan server (Pydantic, sumber kebenaran).
- Pagination dihitung di server; frontend memakai `total` untuk menentukan jumlah halaman.

## Pengungkapan penggunaan AI
Kerangka kode proyek ini dibuat dengan bantuan Claude (Anthropic), sebagaimana diperbolehkan pada ketentuan UTS dengan pengungkapan di README. Saya telah membaca, menjalankan, dan menguji kode ini, serta siap menjelaskannya pada Sesi 8 tanpa bantuan AI.
