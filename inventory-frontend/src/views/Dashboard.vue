<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header"><h2>RIMS Panel</h2></div>
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
        <div class="nav-left"><span class="page-title">{{ activeTab.toUpperCase().replace('-', ' ') }}</span></div>
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
        <div class="dashboard-container">
          
          <div v-if="activeTab === 'dashboard'" class="table-container animate-fade">
          
            <div class="stats-grid">
  <div class="stat-card" @click="activeTab = 'dashboard'">
    <h3>Total Items</h3>
    <p>{{ items.length }}</p>
  </div>
  <div class="stat-card" @click="activeTab = 'request'">
    <h3>Total Requests</h3>
    <p>{{ requests.length }}</p>
  </div>
  <div class="stat-card" @click="activeTab = 'request'">
    <h3>Approved</h3>
    <p>{{ approvedCount }}</p>
  </div>
  <div class="stat-card" @click="activeTab = 'low-stock'">
    <h3>Low Stock</h3>
    <p>{{ lowStockCount }}</p>
  </div>
</div> 
<DashboardCharts 
  :items="items" 
  :requests="requests" 
  :sales="sales" 
  :userRole="userRole" 
/>
            <h1 class="table-title" style="font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif; font-size: 40px; text-align: center;">Live Inventory</h1>
            <table class="table">
  <thead>
    <tr>
      <th>ID</th>
      <th>Name</th>
      <th>Stock Qty</th>
      <th>Price (₹)</th>
      <th v-if="userRole === 'admin'">Action</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="item in items" :key="item.id">
      <td>#{{ item.id }}</td>
      <td>{{ item.name }}</td>
      <td :class="{ 'low-stock-box': (item.current_stock ?? item.quantity) < 5 }">
        {{ item.current_stock ?? item.quantity }}
      </td>
      <td>₹{{ item.price }}</td>

      <td v-if="userRole === 'admin'">
        <button @click="deleteItem(item.id)" class="btn-delete-small">Delete</button>
      </td>
    </tr>
  </tbody>
</table>
          </div>

          <template v-if="userRole === 'admin'">
            <div v-if="activeTab === 'low-stock'" class="table-container animate-fade">
              <h3>Items Requiring Restock (< 5)</h3>
              <table class="table">
                <thead><tr><th>Name</th><th>Current Qty</th></tr></thead>
                <tbody>
                  <tr v-for="item in items.filter(i => (i.current_stock ?? i.quantity) < 5)" :key="item.id">
                    <td>{{ item.name }}</td>
                    <td class="low-stock-box">{{ item.current_stock ?? item.quantity }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="activeTab === 'sales'" class="manage-card animate-fade">
              <h3>Sales Activity</h3>
             <table class="table">
  <thead>
    <tr>
      <th>ID</th>
      <th>Item ID</th>
      <th>Qty</th>
      <th>Price</th>
      <th>Date</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="sale in sales" :key="sale.id">
      <td>#{{ sale.id }}</td>
      <td>{{ sale.reqitem_id }}</td>
      <td>{{ sale.quantity }}</td>
      <td>₹{{ sale.price }}</td>
      <td>{{ new Date(sale.created_at).toLocaleString() }}</td>
    </tr>
  </tbody>
</table>
            </div>
          </template>

          <div v-if="activeTab === 'add' && userRole === 'admin'" class="manage-card animate-fade">
            <h3>Add New Product</h3>
            <div class="form-grid">
              <input v-model="newItem.name" placeholder="Item Name" />
              <input v-model.number="newItem.current_stock" type="number" placeholder="Initial Stock" />
              <input v-model.number="newItem.price" type="number" placeholder="Price (₹)" />
              <button class="btn-add" @click="addItem">Save Product</button>
            </div>
          </div>

          <div v-if="activeTab === 'update' && userRole === 'admin'" class="manage-card animate-fade">
            <h3>Update Existing Item</h3>
            <div class="search-row">
              <input v-model.number="searchId" type="number" placeholder="Enter Item ID" />
              <button class="btn-check" @click="checkAndPrepareUpdate">Check ID</button>
            </div>
            <div v-if="isReadyToUpdate" class="form-grid mt-3">
              <input v-model="updateForm.name" type="text" placeholder="Name" />
              <input v-model.number="updateForm.quantity" type="number" placeholder="Quantity" />
              <input v-model.number="updateForm.price" type="number" placeholder="Price" />
              <div class="action-row">
                <button class="btn-success" @click="confirmUpdate">Save Changes</button>
                <button class="btn-secondary" @click="cancelUpdate">Cancel</button>
              </div>
              
            </div>
          </div>

          <div v-if="activeTab === 'request'" class="manage-card animate-fade">
  <h3>Stock Requests Management</h3>

  <div v-if="userRole === 'user'" class="request-input-box">
    <div class="form-grid">
      <input v-model.number="newRequest.item_id" type="number" placeholder="Item ID" />
      <input v-model.number="newRequest.req_qty" type="number" placeholder="Qty Needed" />
      <button class="btn-check" @click="sendRequest">Submit Request</button>
    </div>
  </div>

  <div class="table-container mt-4">
    <table class="table">
      <thead>
        <tr>
          <th>Req ID</th>
          <th>Item ID</th> <th>Qty</th>
          <th>Status</th>
          <th> Total Price</th>
          <th v-if="userRole === 'admin'">Action</th> </tr>
      </thead>
      <tbody>
        <tr v-for="req in requests" :key="req.id" >
         
          <td>#{{ req.id }}</td>
          <td>{{ req.reqitem_id }}</td> <td>{{ req.quantity }}</td>
          <td>
            <span :class="['status-badge', (req.status || 'pending').toLowerCase()]">
              {{ req.status }}
            </span>
          </td>
          <td>{{ req.quantity }}</td>
          <td>
            ₹{{ calculateTotalPrice(req.reqitem_id, req.quantity) }}  
          </td>
          <td v-if="userRole === 'admin'">
            <div class="action-buttons-mini" v-if="req.status?.toLowerCase() === 'pending'">
              <button @click="handleStatusUpdate(req.id, 'approved')" class="btn-success-sm">Approve</button>
              <button @click="handleStatusUpdate(req.id, 'rejected')" class="btn-delete-small">Reject</button>  
              
  </div>

  <div v-else-if="req.status?.toLowerCase() === 'approved' || req.status?.toLowerCase() === 'rejected'">
    <button @click="deleteRequest(req.id)" class="btn-delete-small">🗑️ Delete Record</button>
  </div>
</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>

import DashboardCharts from '../components/DashboardCharts.vue'
import { ref, onMounted, computed, watch } from 'vue';
import api from '../api'; 
import { useRouter } from 'vue-router';




// Stats Calculation
const approvedCount = computed(() => 
  requests.value.filter(r => r.status?.toLowerCase() === 'approved').length
);

const lowStockCount = computed(() => 
  items.value.filter(i => (i.current_stock ?? i.quantity) < 5).length
);

const items = ref([]);
const sales = ref([]);
const requests = ref([]);
const activeTab = ref('dashboard');
const userRole = localStorage.getItem('role');
const userName = localStorage.getItem('name');
const router = useRouter();

const newItem = ref({ name: '', current_stock: null, price: null });
const newRequest = ref({ reqitem_id: null, req_qty: null, price:null });
const updateForm = ref({ id: null, name: '', quantity: null, price: null });
const searchId = ref(null);
const isReadyToUpdate = ref(false);



watch(activeTab, (newTab) => {
  if (newTab === 'sales') {
    fetchSales();
  }
});
const fetchItems = async () => { try { const res = await api.get('/show'); items.value = res.data; } catch (err) { console.error(err); } };
const fetchRequests = async () => { try { const res = await api.get('/show_requests'); requests.value = res.data; } catch (err) { console.error(err); } };

const addItem = async () => {
  if(!newItem.value.name || !newItem.value.current_stock || !newItem.value.price) {
    alert("Please fill all fields!");
    return;
  }
  
  try { 
    // Backend 'quantity' expect kar raha hai, aap 'current_stock' bhej rahe the
    const dataToSend = {
      name: newItem.value.name,
      quantity: parseInt(newItem.value.current_stock),
      price: parseFloat(newItem.value.price)
    };
    
    await api.post('/item', dataToSend); 
    alert("Item Added!"); 
    fetchItems(); 
    activeTab.value = 'dashboard'; 
    // Reset form
    newItem.value = { name: '', current_stock: null, price: null };
  } 
  catch (err) { 
    console.error(err.response?.data);
    alert("Add Failed: " + (err.response?.data?.detail || "Server Error")); 
  }
};

const checkAndPrepareUpdate = () => {
  const found = items.value.find(i => i.id === searchId.value);
  if (found) { updateForm.value = { id: found.id, name: found.name, quantity: found.quantity, price: found.price }; isReadyToUpdate.value = true; } 
  else { alert("Item ID not found!"); }
};

const confirmUpdate = async () => {
  try { await api.put(`/update/${updateForm.value.id}`, { name: updateForm.value.name, quantity: parseInt(updateForm.value.quantity), price: parseFloat(updateForm.value.price) }); alert("Updated!"); isReadyToUpdate.value = false; fetchItems(); activeTab.value = 'dashboard'; } 
  catch (err) { alert("Update Failed"); }
};

const cancelUpdate = () => { isReadyToUpdate.value = false; searchId.value = null; };

const sendRequest = async () => {
  try { 
    await api.post('/request', { 
        reqitem_id: newRequest.value.item_id, 
        quantity: newRequest.value.req_qty,
        price: 0, // Backend khud item se price utha lega
        status: 'pending' 
    }); 
    alert("Request Sent!"); 
    fetchRequests(); 
    newRequest.value = { item_id: null, req_qty: null }; // Reset form
  } catch (err) { alert("Request Failed: " + err.response?.data?.detail); }
};

// Naya function jo Reject aur Approve dono sambhalega
const handleStatusUpdate = async (id, status) => {
  try {
    if (status === 'approved') {
      // NAYA LOGIC: Approval endpoint ko call karein (Sales entry ke liye)
      await api.post(`/approval/${id}`);
      alert("Request Approved and Sales recorded!");
    } else {
      // Rejection ke liye purana PUT method hi kaafi hai
      await api.put(`/update_request/${id}`, { status: 'rejected' });
      alert("Request Rejected!");
    }
    
    // Refresh data
    fetchRequests(); 
    fetchItems(); 
  } catch (err) { 
    console.error("Action Error:", err.response?.data);
    alert("Action Failed: " + (err.response?.data?.detail || "Check console")); 
  }
};

const handleAccept = async (req) => {
  try {
    // Sirf update_request call karein, wahi stock update kar raha hai
    await api.put(`/update_request/${req.id}`, { status: 'approved' });
    alert("Request Approved!");
    fetchRequests(); 
    fetchItems();
  } catch (err) { alert("Action Failed"); }
};

const deleteItem = async (id) => {
  if (confirm("Are you sure you want to delete this item? This action cannot be undone.")) {
    try {
      const response = await api.delete(`/delete/${id}`);
      
      // Some APIs return 200, others 204. Checking for success:
      if (response.status === 200 || response.status === 204) {
        alert("Item deleted successfully!");
        // Update the local state immediately so the UI reflects the change
        items.value = items.value.filter(item => item.id !== id);
      }
    } catch (err) {
      console.error("Delete Error:", err);
      const errorMsg = err.response?.data?.detail || "Make sure this item isn't linked to existing stock requests.";
      alert("Delete Failed: " + errorMsg);
    }
  }
};
const logout = () => { localStorage.clear(); router.push('/'); };

onMounted(() => { fetchItems(); fetchRequests(); });


const deleteRequest = async (id) => {
  if (confirm("Kya aap is request record ko hamesha ke liye delete karna chahte hain?")) {
    try {
      // Backend endpoint: /delete_request/{request_id}
      const response = await api.delete(`/delete_request/${id}`);
      
      if (response.status === 200) {
        alert("Request record deleted!");
        // Local state update taaki bina refresh kiye UI se hat jaye
        requests.value = requests.value.filter(r => r.id !== id);
      }
    } catch (err) {
      console.error("Delete Request Error:", err);
      alert("Delete Failed: " + (err.response?.data?.detail || "Server error"));
    }
  }
};

const fetchSales = async () => {
  try {
    const res = await api.get('/sales');
    sales.value = res.data;
  } catch (err) {
    console.error(err);
  }
};

// Function to calculate: req.quantity * item.price
const calculateTotalPrice = (itemId, quantity) => {
  // Items list mein se wo item find karein jiska ID match karta ho
  const item = items.value.find(i => i.id === itemId);
  
  if (item) {
    const total = item.price * quantity;
    return total.toLocaleString('en-IN'); // Format: 1,500
  }
  
  return '0'; // Agar item na mile
};

onMounted(() => {
  fetchItems();
  fetchRequests();
  fetchSales();   
});

</script>

