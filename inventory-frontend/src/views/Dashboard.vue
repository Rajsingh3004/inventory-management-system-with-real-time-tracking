<template>
  <div class="app-layout" :class="{ 'sidebar-hidden': !isSidebarOpen }">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>RIMS Panel</h2>
        <button class="toggle-btn" @click="toggleSidebar">❮</button>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">📊 Dashboard</li>
          <li v-if="userRole === 'admin'" :class="{ active: activeTab === 'low-stock' }" @click="activeTab = 'low-stock'">⚠️ Low Stock</li>
          <li v-if="userRole === 'admin'" :class="{ active: activeTab === 'sales' }" @click="activeTab = 'sales'">📈 Sales Report</li>
          <li v-if="userRole === 'admin'" :class="{ active: activeTab === 'add' }" @click="activeTab = 'add'">📦 Add New Item</li>
          <li v-if="userRole === 'admin'" :class="{ active: activeTab === 'update' }" @click="activeTab = 'update'">🔄 Update Stock</li>
          <li :class="{ active: activeTab === 'request' }" @click="activeTab = 'request'">📝 Stock Requests</li>
          <li @click="logout" class="logout-li">🚪 Logout</li>
        </ul>
      </nav>
    </aside>

    <div class="main-wrapper">
      <nav class="top-navbar">
        <div class="nav-left">
          <button v-if="!isSidebarOpen" class="nav-toggle-btn" @click="toggleSidebar">☰</button>
          <span class="page-title">{{ activeTab.toUpperCase().replace('-', ' ') }}</span>
        </div>
        <div class="nav-right">
          <div class="user-profile">
            <div class="avatar">{{ userName?.charAt(0).toUpperCase() }}</div>
            <div class="user-details">
              <span class="name">{{ userName }}</span>&nbsp;
              <span class="role">({{userRole }})</span>
            </div>
          </div>
        </div>
      </nav>

      <main class="main-content">
        <div v-if="activeTab === 'dashboard'" class="animate-fade">
          <div class="stats-grid">
            <div class="stat-card" @click="activeTab = 'dashboard'"><h3>Total Items</h3><p>{{ items.length }}</p></div>
            <div class="stat-card" @click="activeTab = 'request'"  v-if="userRole === 'admin'"><h3>Total Requests</h3><p>{{ requests.length }}</p></div>
            <div class="stat-card" @click="activeTab = 'request'" v-if="userRole === 'admin'"><h3>Approved</h3><p>{{ approvedCount }}</p></div>
            <div class="stat-card" @click="activeTab = 'low-stock'"><h3>Low Stock</h3><p>{{ lowStockCount }}</p></div>
          </div> 
          <DashboardCharts :items="items" :requests="requests" :sales="sales" :userRole="userRole" />
          <div class="table-container mt-4">
            <h1 class="table-title" style="font-family: serif; font-size: 32px; text-align: center;">Live Inventory</h1>
            <table class="table">
              <thead><tr><th>ID</th><th>Name</th><th>Stock</th><th>Price</th><th v-if="userRole === 'admin'">Action</th></tr></thead>
              <tbody>
                <tr v-for="item in items.slice().reverse()" :key="item.id">
                  <td>#{{ item.id }}</td><td>{{ item.name }}</td>
                  <td :class="{ 'low-stock-box': (item.current_stock ?? item.quantity) < 5 }">{{ item.current_stock ?? item.quantity }}</td>
                  <td>₹{{ item.price }}</td>
                  <td v-if="userRole === 'admin'"><button @click="deleteItem(item.id)" class="btn-delete-small">Delete</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="activeTab === 'low-stock' && userRole === 'admin'" class="table-container animate-fade">
          <div class="section-header">
            <h3 style="color: #e74c3c;">⚠️ Low Stock Items (Quantity < 5)</h3>
            <p>In items ko turant restock karne ki zaroorat hai.</p>
          </div>
          <table class="table">
            <thead><tr><th>ID</th><th>Item Name</th><th>Current Stock</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>
              <tr v-for="item in items.filter(i => (i.current_stock ?? i.quantity) < 5).slice().reverse()" :key="item.id">
                <td>#{{ item.id }}</td>
                <td>{{ item.name }}</td>
                <td class="low-stock-box">{{ item.current_stock ?? item.quantity }}</td>
                <td><span class="status-badge rejected">Critical</span></td>
                <td><button @click="openUpdateFromLowStock(item.id)" class="btn-success-sm">Update Now</button></td>
              </tr>
              <tr v-if="items.filter(i => (i.current_stock ?? i.quantity) < 5).length === 0">
                <td colspan="5" style="text-align: center; padding: 20px;">Sab kuch stock mein hai! ✅</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeTab === 'sales' && userRole === 'admin'" class="manage-card animate-fade">
          <h3>Sales Activity History</h3>
          <table class="table">
            <thead><tr><th>Sale ID</th><th>Item ID</th><th>Qty</th><th>Price</th><th>Timestamp</th></tr></thead>
            <tbody>
              <tr v-for="sale in sales.slice().reverse()" :key="sale.id">
                <td>#{{ sale.id }}</td><td>{{ sale.reqitem_id }}</td><td>{{ sale.quantity }}</td><td>₹{{ sale.price }}</td>
                <td>{{ new Date(sale.created_at).toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="activeTab === 'add' && userRole === 'admin'" class="manage-card animate-fade">
          <h3>Add New Product</h3>
          <div class="form-grid">
            <input v-model="newItem.name" placeholder="Item Name" />
            <input v-model.number="newItem.current_stock" type="number" placeholder="Initial Stock" />
            <input v-model.number="newItem.price" type="number" placeholder="Price (₹)" />
            <button class="btn-add" @click="addItem">Save Product</button>
          </div>
          <div class="recent-section mt-4">
            <h4>Recent Additions</h4>
            <table class="table mini-table">
              <tr v-for="item in items.slice().reverse().slice(0, 5)" :key="item.id">
                <td>#{{ item.id }}</td><td>{{ item.name }}</td><td>{{ item.quantity || item.current_stock }}</td>
              </tr>
            </table>
          </div>
        </div>

        <div v-if="activeTab === 'update' && userRole === 'admin'" class="manage-card animate-fade">
          <h3>Update Stock</h3>
          <div class="search-row">
            <input v-model.number="searchId" type="number" placeholder="Enter Item ID" />
            <button class="btn-check" @click="checkAndPrepareUpdate">Check ID</button>
          </div>
          <div v-if="isReadyToUpdate" class="form-grid mt-3">
            <input v-model="updateForm.name" type="text" placeholder="Name" />
            <input v-model.number="updateForm.quantity" type="number" placeholder="Quantity" />
            <input v-model.number="updateForm.price" type="number" placeholder="Price" />
            <button class="btn-success" @click="confirmUpdate">Save Changes</button>
          </div>
          <div class="recent-section mt-4">
            <h4>Inventory Preview (Latest 5)</h4>
            <table class="table mini-table">
              <thead><tr><th>ID</th><th>Name</th><th>Stock</th></tr></thead>
              <tbody>
                <tr v-for="item in items.slice().reverse().slice(0, 5)" :key="item.id">
                  <td>#{{ item.id }}</td><td>{{ item.name }}</td><td>{{ item.quantity || item.current_stock }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="activeTab === 'request'" class="manage-card animate-fade">

  <h3>Requests Management</h3>

  <!-- ✅ USER REQUEST FORM (yaha paste karo) -->
  <div v-if="userRole !== 'admin'" class="form-grid" style="margin-bottom: 20px;">
  
  <select v-model.number="requestForm.reqitem_id">
    <option disabled value="">Select Item</option>
    <option v-for="item in items" :key="item.id" :value="item.id">
      {{ item.name }} (Stock: {{ item.current_stock ?? item.quantity }})
    </option>
  </select>

  <input v-model.number="requestForm.quantity" type="number" placeholder="Quantity" />

  <!-- ✅ STEP 5: ADDRESS INPUT (yaha paste karo) -->
  <input v-model="requestForm.address" placeholder="Enter Address (Satna, Rewa...)" />

  <button class="btn-add" @click="submitRequest">Send Request</button>

</div>
  <!-- 👇 EXISTING TABLE (same rahega) -->
  <table class="table">
    <thead>
  <tr>
    <th>ID</th>
    <th>Item</th>
    <th>Qty</th>
    <th>Price</th>
    <th>Total</th>
    <th>Address</th> <!-- ✅ ADD -->
    <th>Status</th>
    <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="req in requests.slice().reverse()" :key="req.id">
        <td>#{{ req.id }}</td>
        <td>{{ req.reqitem_id }}</td>
        <td>{{ req.quantity }}</td>
        <td>₹{{ req.price }}</td>
        <td>₹{{ req.price * req.quantity }}</td>

<!-- ✅ STEP 8: ADDRESS SHOW -->
        <td>{{ req.address }}</td>
        <td>
          <span :class="['status-badge', (req.status || 'pending').toLowerCase()]">
            {{ req.status }}
          </span>
        </td>
        <td>
          <div v-if="userRole === 'admin'">
            <button v-if="req.status?.toLowerCase() === 'pending'"
              @click="handleStatusUpdate(req.id, 'approved')"
              class="btn-success-sm">Approve</button>

            <button @click="deleteRequest(req.id)"
              class="btn-delete-small">Delete</button>
          </div>
        </td>
      </tr>
    </tbody>
  </table>

</div>
      </main>
    </div>
  </div>
</template>

<script setup>
import DashboardCharts from '../components/DashboardCharts.vue'
import { ref, onMounted, computed } from 'vue';
import api from '../api'; 
import { useRouter } from 'vue-router';

const isSidebarOpen = ref(true);
const activeTab = ref('dashboard');
const items = ref([]);
const sales = ref([]);
const requests = ref([]);
const userRole = localStorage.getItem('role');
const userName = localStorage.getItem('name');
const router = useRouter();

const approvedCount = computed(() => requests.value.filter(r => r.status?.toLowerCase() === 'approved').length);
const lowStockCount = computed(() => items.value.filter(i => (i.current_stock ?? i.quantity) < 5).length);

const newItem = ref({ name: '', current_stock: null, price: null });
const updateForm = ref({ id: null, name: '', quantity: null, price: null });
const requestForm = ref({
  reqitem_id: null,
  quantity: null,
  address: ""
});
const searchId = ref(null);
const isReadyToUpdate = ref(false);

const toggleSidebar = () => { isSidebarOpen.value = !isSidebarOpen.value; };
const fetchItems = async () => { try { const res = await api.get('/show'); items.value = res.data; } catch (err) { console.error(err); } };
const fetchRequests = async () => { try { const res = await api.get('/show_requests'); requests.value = res.data; } catch (err) { console.error(err); } };
const fetchSales = async () => { try { const res = await api.get('/sales'); sales.value = res.data; } catch (err) { console.error(err); } };

const addItem = async () => {
  try {
    await api.post('/item', { name: newItem.value.name, quantity: parseInt(newItem.value.current_stock), price: parseFloat(newItem.value.price) });
    alert("Item Added!"); fetchItems();
    newItem.value = { name: '', current_stock: null, price: null };
  } catch (err) { alert("Add Failed"); }
};

const openUpdateFromLowStock = (id) => {
  searchId.value = id;
  activeTab.value = 'update';
  checkAndPrepareUpdate();
};

const checkAndPrepareUpdate = () => {
  const found = items.value.find(i => i.id === searchId.value);
  if (found) { updateForm.value = { ...found, quantity: found.current_stock ?? found.quantity }; isReadyToUpdate.value = true; }
  else alert("Not found");
};

const confirmUpdate = async () => {
  try {
    await api.put(`/update/${updateForm.value.id}`, { name: updateForm.value.name, quantity: parseInt(updateForm.value.quantity), price: parseFloat(updateForm.value.price) });
    alert("Updated!"); isReadyToUpdate.value = false; fetchItems();
  } catch (err) { alert("Failed"); }
};

const handleStatusUpdate = async (id, status) => {
  try { if (status === 'approved') await api.post(`/approval/${id}`); fetchRequests(); fetchItems(); } 
  catch (err) { alert("Failed"); }
};

const submitRequest = async () => {
  if (!requestForm.value.reqitem_id || !requestForm.value.quantity) {
    alert("Please fill all fields ⚠️");
    return;
  }

  try {
   await api.post('/request', {
  reqitem_id: requestForm.value.reqitem_id,
  quantity: requestForm.value.quantity,
  address: requestForm.value.address
});
    
    alert("Request Sent Successfully ✅");

    requestForm.value = {
      reqitem_id: null,
      quantity: null
    };

    fetchRequests();

  } catch (err) {
    console.error(err);
    alert(err.response?.data?.detail || "Request Failed ❌");
  }
};

const deleteItem = async (id) => { if(confirm("Delete?")) { await api.delete(`/delete/${id}`); fetchItems(); } };
const deleteRequest = async (id) => { if(confirm("Delete request?")) { await api.delete(`/delete_request/${id}`); fetchRequests(); } };
const logout = () => { localStorage.clear(); router.push('/'); };

onMounted(() => { fetchItems(); fetchRequests(); fetchSales(); });
</script>

<style scoped>
.app-layout { display: flex; min-height: 100vh; background: #f4f7f6; transition: 0.3s; }
.sidebar { width: 260px; background: #2c3e50; color: white; transition: 0.3s; }
.sidebar-hidden .sidebar { margin-left: -260px; }
.main-wrapper { flex: 1; min-width: 0; }
.top-navbar { background: white; padding: 15px; display: flex; justify-content: space-between; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; padding: 15px; }
.stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; cursor: pointer; border-bottom: 4px solid #3498db; }
.table-container, .manage-card { background: white; padding: 20px; margin: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px; border-bottom: 1px solid #eee; text-align: left; }
.btn-delete-small { background: #ff7675; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
.btn-success-sm { background: #55efc4; color: #00b894; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }
.status-badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
.status-badge.approved { background: #d4edda; color: #155724; }
.status-badge.pending { background: #fff3cd; color: #856404; }
.status-badge.rejected { background: #f8d7da; color: #d63031; }
.low-stock-box { background: #ffebee; color: #c62828; font-weight: bold; border-radius: 4px; padding: 5px; }
.animate-fade { animation: fadeIn 0.4s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>