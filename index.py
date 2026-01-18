from flask import Flask, render_template_string, request, jsonify, send_file
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os
import json

app = Flask(__name__)

# MongoDB Connection
MONGODB_URI = "mongodb+srv://dsadeepa02_db_user:zero8907@cluster0.nfiluqd.mongodb.net/jeenu_motors?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGODB_URI)
db = client.jeenu_motors

# HTML Template (All pages in one)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jeenu Motors - Billing System</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f7fafc;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin: 0; }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .tab-btn {
            padding: 12px 24px;
            border: none;
            background: white;
            cursor: pointer;
            border-radius: 5px;
            font-size: 16px;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .tab-btn.active {
            background: #667eea;
            color: white;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .input, .textarea {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        .btn {
            padding: 10px 20px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-success { background: #48bb78; color: white; }
        .btn-success:hover { background: #38a169; }
        .btn-danger { background: #f56565; color: white; }
        .btn-danger:hover { background: #e53e3e; }
        .btn-secondary { background: #718096; color: white; }
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .service-card {
            border: 2px solid #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        .service-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
        }
        .service-img {
            width: 100%;
            height: 120px;
            object-fit: cover;
            border-radius: 5px;
            margin-bottom: 10px;
            background: #edf2f7;
        }
        .selected-service {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            margin: 10px 0;
        }
        .selected-service input {
            width: 100px;
            padding: 5px;
            margin-right: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        th {
            background: #f7fafc;
            font-weight: bold;
        }
        .bill-preview {
            background: white;
            padding: 40px;
            border-radius: 10px;
            margin: 20px 0;
        }
        @media print {
            body * { visibility: hidden; }
            .bill-preview, .bill-preview * { visibility: visible; }
            .bill-preview { position: absolute; left: 0; top: 0; }
            .no-print { display: none !important; }
        }
        .img-preview {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>JEENU MOTORS</h1>
            <p>Three Wheeler Repair Shop - Billing System</p>
        </div>

        <div class="tabs no-print">
            <button class="tab-btn active" onclick="showTab('billing')">Create Bill</button>
            <button class="tab-btn" onclick="showTab('services')">Manage Services</button>
            <button class="tab-btn" onclick="showTab('bills')">View Bills</button>
        </div>

        <!-- BILLING TAB -->
        <div id="billing" class="tab-content active">
            <div class="card">
                <h2>Customer Details</h2>
                <input class="input" id="customerName" placeholder="Customer Name *" required>
                <input class="input" id="phone" placeholder="Phone Number">
                <input class="input" id="vehicleNo" placeholder="Vehicle Number">
            </div>

            <div class="card">
                <h2>Select Services</h2>
                <div class="service-grid" id="serviceGrid"></div>
            </div>

            <div class="card">
                <h2>Selected Services</h2>
                <div id="selectedServices"></div>
                <h3 style="text-align: right; margin-top: 20px;">Total: ₹<span id="totalAmount">0.00</span></h3>
                <button class="btn btn-success" onclick="generateBill()" style="width: 100%; font-size: 1.2em; margin-top: 10px;">
                    Generate Bill
                </button>
            </div>

            <div id="billPreviewSection" style="display: none;">
                <div class="bill-preview" id="billPreview"></div>
                <div class="no-print" style="text-align: center;">
                    <button class="btn btn-primary" onclick="window.print()">🖨️ Print Bill</button>
                    <button class="btn btn-success" onclick="resetBilling()">✨ New Bill</button>
                </div>
            </div>
        </div>

        <!-- SERVICES TAB -->
        <div id="services" class="tab-content">
            <div class="card">
                <h2 id="serviceFormTitle">Add New Service</h2>
                <form id="serviceForm" onsubmit="saveService(event)">
                    <input class="input" id="serviceName" placeholder="Service Name *" required>
                    <input class="input" type="number" step="0.01" id="servicePrice" placeholder="Default Price (₹) *" required>
                    <input class="input" id="serviceImage" placeholder="Image URL (optional)">
                    <button class="btn btn-primary" type="submit">Add Service</button>
                    <button class="btn btn-secondary" type="button" onclick="cancelEdit()" id="cancelBtn" style="display: none;">Cancel</button>
                </form>
            </div>

            <div class="card">
                <h2>All Services</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Price</th>
                            <th>Image</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="servicesTable"></tbody>
                </table>
            </div>
        </div>

        <!-- BILLS TAB -->
        <div id="bills" class="tab-content">
            <div class="card">
                <h2>Recent Bills</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Bill No</th>
                            <th>Date</th>
                            <th>Customer</th>
                            <th>Total</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="billsTable"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let services = [];
        let selectedServices = [];
        let editingServiceId = null;

        // Tab switching
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'billing') loadServices();
            if (tabName === 'services') loadAllServices();
            if (tabName === 'bills') loadBills();
        }

        // Load services for billing
        async function loadServices() {
            const res = await fetch('/api/services');
            services = await res.json();
            renderServiceGrid();
        }

        function renderServiceGrid() {
            const grid = document.getElementById('serviceGrid');
            grid.innerHTML = services.map(s => `
                <div class="service-card" onclick='addServiceToBill(${JSON.stringify(s).replace(/'/g, "&apos;")})'>
                    ${s.image ? `<img src="${s.image}" class="service-img" alt="${s.name}">` : '<div class="service-img"></div>'}
                    <h3>${s.name}</h3>
                    <p style="color: #667eea; font-weight: bold;">₹${s.defaultPrice}</p>
                </div>
            `).join('');
        }

        function addServiceToBill(service) {
            selectedServices.push({
                id: Date.now(),
                serviceId: service._id,
                name: service.name,
                price: service.defaultPrice,
                image: service.image
            });
            renderSelectedServices();
        }

        function renderSelectedServices() {
            const container = document.getElementById('selectedServices');
            container.innerHTML = selectedServices.map(s => `
                <div class="selected-service">
                    <span>${s.name}</span>
                    <div>
                        <input type="number" step="0.01" value="${s.price}" 
                               onchange="updatePrice(${s.id}, this.value)">
                        <button class="btn btn-danger" onclick="removeService(${s.id})">Remove</button>
                    </div>
                </div>
            `).join('');
            updateTotal();
        }

        function updatePrice(id, price) {
            const service = selectedServices.find(s => s.id === id);
            if (service) service.price = parseFloat(price) || 0;
            updateTotal();
        }

        function removeService(id) {
            selectedServices = selectedServices.filter(s => s.id !== id);
            renderSelectedServices();
        }

        function updateTotal() {
            const total = selectedServices.reduce((sum, s) => sum + s.price, 0);
            document.getElementById('totalAmount').textContent = total.toFixed(2);
        }

        async function generateBill() {
            const customerName = document.getElementById('customerName').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const vehicleNo = document.getElementById('vehicleNo').value.trim();

            if (!customerName || selectedServices.length === 0) {
                alert('Please enter customer name and add at least one service');
                return;
            }

            const total = selectedServices.reduce((sum, s) => sum + s.price, 0);
            const billData = {
                customerName,
                phone,
                vehicleNo,
                services: selectedServices,
                total
            };

            const res = await fetch('/api/bills', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(billData)
            });

            const bill = await res.json();
            displayBill(bill);
        }

        function displayBill(bill) {
            const preview = document.getElementById('billPreview');
            preview.innerHTML = `
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="margin: 0;">JEENU MOTORS</h1>
                    <p>Three Wheeler Repair Shop</p>
                    <hr style="margin: 20px 0;">
                </div>
                <p><strong>Bill No:</strong> ${bill.billNo}</p>
                <p><strong>Date:</strong> ${new Date(bill.createdAt).toLocaleString()}</p>
                <hr style="margin: 20px 0;">
                <p><strong>Customer:</strong> ${bill.customerName}</p>
                <p><strong>Phone:</strong> ${bill.phone || '-'}</p>
                <p><strong>Vehicle:</strong> ${bill.vehicleNo || '-'}</p>
                <hr style="margin: 20px 0;">
                <h3>Services:</h3>
                <table style="width: 100%; margin-top: 10px;">
                    <thead>
                        <tr>
                            <th>Service</th>
                            <th style="text-align: right;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${bill.services.map(s => `
                            <tr>
                                <td>${s.name}</td>
                                <td style="text-align: right;">₹${s.price.toFixed(2)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <hr style="margin: 20px 0;">
                <h2 style="text-align: right;">Total: ₹${bill.total.toFixed(2)}</h2>
                <div style="text-align: center; margin-top: 40px;">
                    <p>Thank you for your business!</p>
                    <p>Visit Again!</p>
                </div>
            `;
            document.getElementById('billPreviewSection').style.display = 'block';
            document.querySelector('.tabs').style.display = 'none';
            document.querySelector('[id="billing"] .card').forEach(c => c.style.display = 'none');
        }

        function resetBilling() {
            document.getElementById('customerName').value = '';
            document.getElementById('phone').value = '';
            document.getElementById('vehicleNo').value = '';
            selectedServices = [];
            renderSelectedServices();
            document.getElementById('billPreviewSection').style.display = 'none';
            document.querySelector('.tabs').style.display = 'flex';
            document.querySelectorAll('[id="billing"] .card').forEach(c => c.style.display = 'block');
        }

        // Service Management
        async function loadAllServices() {
            const res = await fetch('/api/services');
            services = await res.json();
            renderServicesTable();
        }

        function renderServicesTable() {
            const tbody = document.getElementById('servicesTable');
            tbody.innerHTML = services.map(s => `
                <tr>
                    <td>${s.name}</td>
                    <td>₹${s.defaultPrice}</td>
                    <td>${s.image ? `<img src="${s.image}" class="img-preview">` : '-'}</td>
                    <td>
                        <button class="btn btn-primary" onclick='editService(${JSON.stringify(s).replace(/'/g, "&apos;")})'>Edit</button>
                        <button class="btn btn-danger" onclick="deleteService('${s._id}')">Delete</button>
                    </td>
                </tr>
            `).join('');
        }

        async function saveService(e) {
            e.preventDefault();
            const name = document.getElementById('serviceName').value;
            const defaultPrice = parseFloat(document.getElementById('servicePrice').value);
            const image = document.getElementById('serviceImage').value;

            const data = { name, defaultPrice, image };

            if (editingServiceId) {
                await fetch('/api/services', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...data, id: editingServiceId })
                });
            } else {
                await fetch('/api/services', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            }

            cancelEdit();
            loadAllServices();
        }

        function editService(service) {
            editingServiceId = service._id;
            document.getElementById('serviceName').value = service.name;
            document.getElementById('servicePrice').value = service.defaultPrice;
            document.getElementById('serviceImage').value = service.image || '';
            document.getElementById('serviceFormTitle').textContent = 'Edit Service';
            document.getElementById('cancelBtn').style.display = 'inline-block';
        }

        function cancelEdit() {
            editingServiceId = null;
            document.getElementById('serviceForm').reset();
            document.getElementById('serviceFormTitle').textContent = 'Add New Service';
            document.getElementById('cancelBtn').style.display = 'none';
        }

        async function deleteService(id) {
            if (confirm('Delete this service?')) {
                await fetch(`/api/services?id=${id}`, { method: 'DELETE' });
                loadAllServices();
            }
        }

        // Bills History
        async function loadBills() {
            const res = await fetch('/api/bills');
            const bills = await res.json();
            renderBillsTable(bills);
        }

        function renderBillsTable(bills) {
            const tbody = document.getElementById('billsTable');
            tbody.innerHTML = bills.map(b => `
                <tr>
                    <td>${b.billNo}</td>
                    <td>${new Date(b.createdAt).toLocaleDateString()}</td>
                    <td>${b.customerName}</td>
                    <td>₹${b.total.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-primary" onclick='viewBill(${JSON.stringify(b).replace(/'/g, "&apos;")})'>View</button>
                    </td>
                </tr>
            `).join('');
        }

        function viewBill(bill) {
            showTab('billing');
            displayBill(bill);
        }

        // Load initial services
        loadServices();
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/services', methods=['GET', 'POST', 'PUT', 'DELETE'])
def services():
    if request.method == 'GET':
        services = list(db.services.find())
        for service in services:
            service['_id'] = str(service['_id'])
        return jsonify(services)
    
    elif request.method == 'POST':
        data = request.json
        result = db.services.insert_one({
            'name': data['name'],
            'defaultPrice': float(data['defaultPrice']),
            'image': data.get('image', ''),
            'createdAt': datetime.now()
        })
        return jsonify({'_id': str(result.inserted_id)})
    
    elif request.method == 'PUT':
        data = request.json
        db.services.update_one(
            {'_id': ObjectId(data['id'])},
            {'$set': {
                'name': data['name'],
                'defaultPrice': float(data['defaultPrice']),
                'image': data.get('image', ''),
                'updatedAt': datetime.now()
            }}
        )
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        service_id = request.args.get('id')
        db.services.delete_one({'_id': ObjectId(service_id)})
        return jsonify({'success': True})

@app.route('/api/bills', methods=['GET', 'POST'])
def bills():
    if request.method == 'POST':
        data = request.json
        
        # Get or create counter
        counter = db.counters.find_one_and_update(
            {'_id': 'billNumber'},
            {'$inc': {'seq': 1}},
            upsert=True,
            return_document=True
        )
        
        seq = counter.get('seq', 1) if counter else 1
        bill_no = f"JM{datetime.now().strftime('%Y%m%d')}{str(seq).zfill(3)}"
        
        bill = {
            'billNo': bill_no,
            'customerName': data['customerName'],
            'phone': data.get('phone', ''),
            'vehicleNo': data.get('vehicleNo', ''),
            'services': data['services'],
            'total': float(data['total']),
            'createdAt': datetime.now()
        }
        
        result = db.bills.insert_one(bill)
        bill['_id'] = str(result.inserted_id)
        return jsonify(bill)
    
    elif request.method == 'GET':
        bills = list(db.bills.find().sort('createdAt', -1).limit(50))
        for bill in bills:
            bill['_id'] = str(bill['_id'])
        return jsonify(bills)

# Vercel serverless function handler
app.debug = False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
