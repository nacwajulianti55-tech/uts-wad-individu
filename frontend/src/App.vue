<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { api } from './api'

const PAGE_SIZE = 5

// --- daftar: empat state (loading / error / empty / success) ---
const status = ref('loading')
const errorMsg = ref('')
const items = ref([])
const total = ref(0)
const page = ref(1)
const search = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

async function load() {
  status.value = 'loading'
  try {
    const data = await api.list({ page: page.value, pageSize: PAGE_SIZE, search: search.value })
    items.value = data.items
    total.value = data.total
    if (data.items.length === 0 && page.value > 1) {
      page.value = Math.max(1, Math.ceil(data.total / PAGE_SIZE))
      return load()
    }
    status.value = data.items.length === 0 ? 'empty' : 'success'
  } catch (e) {
    errorMsg.value = e.message === 'Failed to fetch' ? 'Tidak dapat terhubung ke server.' : e.message
    status.value = 'error'
  }
}

let timer
watch(search, () => {
  clearTimeout(timer)
  timer = setTimeout(() => {
    page.value = 1
    load()
  }, 300)
})

function goto(p) {
  page.value = p
  load()
}

onMounted(load)

// --- form create dengan validasi ---
const form = reactive({ route: '', driver: '', departure: '', capacity: '', booked: 0 })
const errors = reactive({})
const submitting = ref(false)
const serverError = ref('')

function validate() {
  Object.keys(errors).forEach((k) => delete errors[k])
  const route = form.route.trim()
  const driver = form.driver.trim()
  if (route.length < 3) errors.route = 'Rute minimal 3 karakter'
  if (driver.length < 2) errors.driver = 'Nama sopir minimal 2 karakter'
  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(form.departure)) errors.departure = 'Format jam HH:MM (mis. 07:30)'
  const cap = Number(form.capacity)
  const bk = Number(form.booked)
  if (!Number.isInteger(cap) || cap < 1 || cap > 60) errors.capacity = 'Kapasitas 1–60'
  if (!Number.isInteger(bk) || bk < 0) errors.booked = 'Terpesan tidak boleh negatif'
  else if (!errors.capacity && bk > cap) errors.booked = 'Terpesan tidak boleh melebihi kapasitas'
  return Object.keys(errors).length === 0
}

async function submit() {
  serverError.value = ''
  if (!validate()) return
  submitting.value = true
  try {
    await api.create({
      route: form.route.trim(),
      driver: form.driver.trim(),
      departure: form.departure,
      capacity: Number(form.capacity),
      booked: Number(form.booked),
    })
    Object.assign(form, { route: '', driver: '', departure: '', capacity: '', booked: 0 })
    search.value = ''
    page.value = 1
    await load()
  } catch (e) {
    serverError.value = e.message
  } finally {
    submitting.value = false
  }
}

// --- hapus dengan konfirmasi ---
async function remove(item) {
  if (!window.confirm(`Hapus sesi "${item.route}" (${item.departure})?`)) return
  try {
    await api.remove(item.id)
    await load()
  } catch (e) {
    window.alert(e.message)
  }
}
</script>

<template>
  <main class="wrap">
    <h1>Shuttle Kampus</h1>

    <section class="card">
      <h2>Tambah sesi</h2>
      <div class="grid">
        <label>Rute
          <input v-model="form.route" placeholder="Asrama - Fakultas Teknik" />
          <small v-if="errors.route" class="err">{{ errors.route }}</small>
        </label>
        <label>Sopir
          <input v-model="form.driver" placeholder="Pak Andi" />
          <small v-if="errors.driver" class="err">{{ errors.driver }}</small>
        </label>
        <label>Berangkat (HH:MM)
          <input v-model="form.departure" placeholder="07:30" />
          <small v-if="errors.departure" class="err">{{ errors.departure }}</small>
        </label>
        <label>Kapasitas
          <input v-model="form.capacity" type="number" min="1" max="60" />
          <small v-if="errors.capacity" class="err">{{ errors.capacity }}</small>
        </label>
        <label>Terpesan
          <input v-model="form.booked" type="number" min="0" />
          <small v-if="errors.booked" class="err">{{ errors.booked }}</small>
        </label>
      </div>
      <p v-if="serverError" class="err">{{ serverError }}</p>
      <button :disabled="submitting" @click="submit">{{ submitting ? 'Menyimpan…' : 'Simpan' }}</button>
    </section>

    <section class="card">
      <h2>Daftar sesi</h2>
      <input v-model="search" class="search" placeholder="Cari rute atau sopir…" />

      <p v-if="status === 'loading'" class="info">Memuat data…</p>

      <div v-else-if="status === 'error'" class="info">
        <p class="err">{{ errorMsg }}</p>
        <button @click="load">Coba lagi</button>
      </div>

      <p v-else-if="status === 'empty'" class="info">
        {{ search ? 'Tidak ada sesi yang cocok dengan pencarian.' : 'Belum ada sesi.' }}
      </p>

      <template v-else>
        <table>
          <thead>
            <tr><th>Rute</th><th>Sopir</th><th>Berangkat</th><th>Terisi</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="s in items" :key="s.id">
              <td>{{ s.route }}</td>
              <td>{{ s.driver }}</td>
              <td>{{ s.departure }}</td>
              <td>
                {{ s.booked }}/{{ s.capacity }}
                <span v-if="s.booked >= s.capacity" class="badge">Penuh</span>
              </td>
              <td><button class="danger" @click="remove(s)">Hapus</button></td>
            </tr>
          </tbody>
        </table>
        <div class="pager">
          <button :disabled="page <= 1" @click="goto(page - 1)">‹ Sebelumnya</button>
          <span>Halaman {{ page }} / {{ totalPages }} · {{ total }} sesi</span>
          <button :disabled="page >= totalPages" @click="goto(page + 1)">Berikutnya ›</button>
        </div>
      </template>
    </section>
  </main>
</template>

<style>
body { font-family: system-ui, sans-serif; background: #f4f5f7; margin: 0; color: #1f2933; }
.wrap { max-width: 860px; margin: 0 auto; padding: 24px 16px; }
.card { background: #fff; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-bottom: 12px; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 14px; }
input { padding: 8px; border: 1px solid #cbd2d9; border-radius: 6px; font-size: 14px; }
.search { width: 100%; box-sizing: border-box; margin-bottom: 12px; }
button { padding: 8px 14px; border: 0; border-radius: 6px; background: #2563eb; color: #fff; cursor: pointer; }
button:disabled { opacity: .5; cursor: not-allowed; }
button.danger { background: #dc2626; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { text-align: left; padding: 8px; border-bottom: 1px solid #e4e7eb; }
.err { color: #dc2626; font-size: 13px; }
.info { text-align: center; padding: 20px 0; color: #52606d; }
.badge { background: #fee2e2; color: #b91c1c; border-radius: 4px; padding: 1px 6px; font-size: 12px; margin-left: 6px; }
.pager { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; font-size: 14px; }
</style>
