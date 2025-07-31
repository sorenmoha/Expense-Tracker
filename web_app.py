from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import datetime

from month import Month
from utils import load_data, save_data

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Budget Tracker - Dark Theme</title>
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #0f1419;
            color: #e6e9ef;
            font-size: 18px;
            line-height: 1.6;
        }

        .header {
            background: #1a1f3a;
            color: #ffffff;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            border-bottom: 1px solid #2d3748;
        }

        .header h1 { 
            font-size: 3rem; 
            margin-bottom: 15px; 
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        .container { 
            text-align: center;
            margin: 0 auto; 
            padding: 30px 30px;
        }

        .actions-bar {
            background: #1e2328;
            padding: 20px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            margin: 0 auto 30px auto;
            display: flex;
            gap: 15px;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            border: 1px solid #2d3748;
            width: fit-content;
        }

        .btn {
            background: #4ade80;
            color: #000000;
            border: none;
            padding: 14px 28px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            min-height: 48px;
            font-family: inherit;
            box-shadow: 0 2px 8px rgba(74, 222, 128, 0.2);
        }

        .btn:hover {
            background: #22c55e;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(74, 222, 128, 0.4);
        }

        .btn-danger { 
            background: #ef4444; 
            color: #ffffff;
        }
        .btn-danger:hover { 
            background: #dc2626;
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
        }

        .btn-secondary { 
            background: #6b7280; 
            color: #ffffff;
        }
        .btn-secondary:hover { 
            background: #4b5563;
            box-shadow: 0 6px 20px rgba(107, 114, 128, 0.4);
        }

        .btn-info { 
            background: #06b6d4; 
            color: #ffffff;
        }
        .btn-info:hover { 
            background: #0891b2;
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
        }

        .btn-small { 
            padding: 10px 20px; 
            font-size: 16px; 
            margin: 0 6px;
            min-height: 40px;
        }

        .spreadsheet-container {
            display: inline-block;
            background: #1e2328;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            border: 1px solid #2d3748;
            
        }

        .spreadsheet-table {
            border-collapse: collapse;
            font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Monaco', monospace;
            font-size: 17px;
            
        }

        .spreadsheet-table th {
            background: #2d3748;
            color: #f7fafc;
            padding: 20px 18px;
            text-align: left;
            font-weight: 700;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #4a5568;
            border-right: 1px solid #4a5568;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .spreadsheet-table td {
            padding: 18px 16px;
            border-bottom: 1px solid #2d3748;
            border-right: 1px solid #2d3748;
            font-size: 17px;
            white-space: nowrap;
        }

        .spreadsheet-table tbody tr:hover { 
            background: #2d3748; 
        }
        .spreadsheet-table tbody tr:nth-child(even) { 
            background: #1a202c; 
        }

        .month-cell { 
            font-weight: 700; 
            color: #90cdf4; 
            background: #2a4365 !important; 
            font-size: 18px;
        }

        .currency { 
            text-align: right; 
            font-family: 'JetBrains Mono', monospace; 
            font-weight: 600; 
            font-size: 17px;
        }
        .currency.positive { color: #68d391; }
        .currency.negative { color: #fc8181; }
        .total-row { 
            background: #2d4a22 !important; 
            font-weight: 700; 
            color: #c6f6d5;
        }
        .actions-cell { 
            text-align: center; 
            padding: 18px 30px !important;
        }

        .month-cell:hover {
            background: #3182ce !important;
            cursor: pointer;
            text-decoration: underline;
        }

        .summary-modal, .form-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(8px);
            overflow-y: auto;
        }

        .summary-content, .modal-content {
            background: #1e2328;
            margin: 2% auto;
            padding: 0;
            border-radius: 20px;
            width: 90%;
            max-width: 900px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.6);
            border: 1px solid #2d3748;
            max-height: 90vh;
            overflow-y: auto;
        }

        .modal-content {
            padding: 40px;
            max-width: 700px;
        }

        .summary-header {
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            color: #ffffff;
            padding: 30px;
            border-radius: 20px 20px 0 0;
            text-align: center;
        }
        
        .summary-body {
            padding: 40px;
            font-family: 'Open Sans', Arial, sans-serif;
            line-height: 1.8;
            font-size: 18px;
        }

        .summary-section {
            margin-bottom: 30px;
            padding: 25px;
            background: #2d3748;
            border-radius: 12px;
            border-left: 5px solid #4299e1;
        }

        .summary-section h3 {
            color: #f7fafc;
            margin-bottom: 20px;
            font-family: 'Inter', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-size: 16px;
            font-weight: 700;
        }

        .cost-line {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px dotted #4a5568;
            font-size: 18px;
        }

        .cost-line:last-child {
            border-bottom: none;
            font-weight: bold;
            margin-top: 15px;
            padding-top: 20px;
            border-top: 2px solid #4299e1;
        }

        .additional-costs-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 18px;
        }

        .additional-costs-table th {
            background: #2d3748;
            padding: 18px;
            text-align: left;
            font-weight: 700;
            border: 1px solid #4a5568;
            font-size: 18px;
            color: #f7fafc;
        }

        .additional-costs-table td {
            padding: 18px;
            border: 1px solid #4a5568;
            font-size: 18px;
            vertical-align: middle;
            background: #1e2328;
        }

        .grand-total {
            background: linear-gradient(135deg, #2f855a 0%, #38a169 100%);
            color: #ffffff;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            margin-top: 25px;
        }

        .message {
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            font-weight: 600;
            font-size: 18px;
        }
        
        .message.success { 
            background: #2f855a; 
            color: #ffffff; 
            border: 1px solid #38a169; 
        }
        
        .message.error { 
            background: #e53e3e; 
            color: #ffffff; 
            border: 1px solid #c53030; 
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin: 25px 0;
        }

        .form-group { 
            display: flex; 
            flex-direction: column; 
        }
        
        .form-group label { 
            font-weight: 700; 
            margin-bottom: 12px; 
            color: #f7fafc; 
            font-size: 18px;
        }
        
        .form-group input {
            padding: 18px;
            border: 2px solid #4a5568;
            border-radius: 12px;
            font-size: 20px;
            transition: all 0.3s ease;
            min-height: 60px;
            background: #2d3748;
            color: #e2e8f0;
            font-family: inherit;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #4299e1;
            box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.2);
            background: #1a202c;
        }

        .form-group input::placeholder {
            color: #a0aec0;
        }

        .close {
            color: #a0aec0;
            float: right;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
        }
        .close:hover { color: #ffffff; }

        .loading { 
            text-align: center; 
            padding: 60px; 
            color: #a0aec0; 
        }
        .spinner {
            border: 4px solid #2d3748;
            border-top: 4px solid #4299e1;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 25px;
        }
        @keyframes spin { 
            0% { transform: rotate(0deg); } 
            100% { transform: rotate(360deg); } 
        }

        .empty-state { 
            text-align: center; 
            padding: 80px 30px; 
            color: #a0aec0; 
        }
        .empty-state h3 { 
            margin-bottom: 15px; 
            color: #e2e8f0; 
            font-size: 24px;
        }
        .empty-state p {
            font-size: 18px;
        }

        h2 {
            color: #f7fafc;
            font-size: 28px;
            margin-bottom: 20px;
        }

        h3 {
            color: #f7fafc;
            font-size: 22px;
            margin-bottom: 15px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }
            
            .header h1 {
                font-size: 2.5rem;
            }
            
            .actions-bar {
                flex-direction: column;
                align-items: stretch;
                gap: 15px;
            }
            
            .btn {
                width: 100%;
                justify-content: center;
                padding: 18px 25px;
                font-size: 18px;
            }
            
            .spreadsheet-container {
                overflow-x: auto;
                border-radius: 12px;
                -webkit-overflow-scrolling: touch;
            }
            
            .spreadsheet-table {
                min-width: 1200px;
                font-size: 16px;
            }
            
            .spreadsheet-table th {
                padding: 16px 12px;
                font-size: 14px;
            }
            
            .spreadsheet-table td {
                padding: 16px 12px;
                font-size: 16px;
            }
            
            .form-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .modal-content {
                margin: 5% auto;
                padding: 30px;
                width: 95%;
                max-height: 85vh;
            }
            
            .form-group input {
                padding: 16px;
                font-size: 18px;
                min-height: 55px;
            }
            
            .additional-costs-table {
                font-size: 16px;
            }
            
            .additional-costs-table th,
            .additional-costs-table td {
                padding: 14px 10px;
                font-size: 16px;
            }
        }

        @media (max-width: 480px) {
            .spreadsheet-table {
                font-size: 15px;
            }
            
            .spreadsheet-table th {
                padding: 14px 8px;
                font-size: 13px;
            }
            
            .spreadsheet-table td {
                padding: 14px 8px;
                font-size: 15px;
            }
            
            .btn-small {
                padding: 8px 16px;
                font-size: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Expense Tracker</h1>
    </div>

    <div class="container">
        <div class="actions-bar">
            <button class="btn" onclick="openModal()">Add New Month</button>
            <button class="btn btn-secondary" onclick="loadMonths()">Refresh Data</button>
            <button class="btn btn-secondary" onclick="exportData()">Export CSV</button>
        </div>

        <div id="message"></div>

        <div class="spreadsheet-container">
            <div id="loading" class="loading">
                <div class="spinner"></div>
                Loading your budget data...
            </div>

            <table class="spreadsheet-table" id="budgetTable" style="display: none;">
                <thead>
                    <tr>
                        <th>Month</th>
                        <th>Rent</th>
                        <th>Heating</th>
                        <th>Electric</th>
                        <th>Water</th>
                        <th>Internet</th>
                        <th>Addtl. Costs</th>
                        <th>All Utilities</th>
                        <th>Your Share</th>
                        <th>Housing Total</th>
                        <th>Monthly Total</th>
                        <th>Paid</th>
                        <th>Owed</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="budgetTableBody"></tbody>
            </table>

            <div id="emptyState" class="empty-state" style="display: none;">
                <h3>No Budget Data Yet</h3>
                <p>Click "Add New Month" to get started with your budget tracking!</p>
            </div>
        </div>
    </div>

    <div id="summaryModal" class="summary-modal">
        <div class="summary-content">
            <div class="summary-header">
                <span class="close" onclick="closeSummaryModal()" style="float: right; font-size: 28px; cursor: pointer;">&times;</span>
                <h2 id="summaryTitle">Month Summary</h2>
            </div>
            <div class="summary-body" id="summaryBody"></div>
        </div>
    </div>

    <div id="monthModal" class="form-modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2>Add New Month</h2>
            <form id="monthForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="monthName">Month (YYYY-MM)</label>
                        <input type="text" id="monthName" placeholder="2025-02" required>
                    </div>
                    <div class="form-group">
                        <label for="rent">Rent ($)</label>
                        <input type="number" id="rent" step="0.01" placeholder="1200.00" required>
                    </div>
                    <div class="form-group">
                        <label for="heating">Heating ($)</label>
                        <input type="number" id="heating" step="0.01" placeholder="80.00" required>
                    </div>
                    <div class="form-group">
                        <label for="electric">Electric ($)</label>
                        <input type="number" id="electric" step="0.01" placeholder="70.00" required>
                    </div>
                    <div class="form-group">
                        <label for="water">Water ($)</label>
                        <input type="number" id="water" step="0.01" placeholder="40.00" required>
                    </div>
                    <div class="form-group">
                        <label for="internet">Internet ($)</label>
                        <input type="number" id="internet" step="0.01" placeholder="60.00" required>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 35px;">
                    <button type="submit" class="btn">Create Month</button>
                    <button type="button" class="btn btn-secondary" onclick="closeModal()" style="margin-left: 15px;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <div id="editModal" class="form-modal">
        <div class="modal-content" style="max-width: 1000px;">
            <span class="close" onclick="closeEditModal()">&times;</span>
            <h2>Edit Month: <span id="editMonthName"></span></h2>
            
            <div class="form-grid">
                <div class="form-group">
                    <label for="editRent">Rent ($)</label>
                    <input type="number" id="editRent" step="0.01" required>
                </div>
                <div class="form-group">
                    <label for="editHeating">Heating ($)</label>
                    <input type="number" id="editHeating" step="0.01" required>
                </div>
                <div class="form-group">
                    <label for="editElectric">Electric ($)</label>
                    <input type="number" id="editElectric" step="0.01" required>
                </div>
                <div class="form-group">
                    <label for="editWater">Water ($)</label>
                    <input type="number" id="editWater" step="0.01" required>
                </div>
                <div class="form-group">
                    <label for="editInternet">Internet ($)</label>
                    <input type="number" id="editInternet" step="0.01" required>
                </div>
            </div>

            <div style="margin-top: 35px;">
                <h3>Additional Costs</h3>
                <button type="button" class="btn btn-secondary" onclick="openAddCostModal()" style="margin-bottom: 20px;">Add Additional Cost</button>
                
                <table class="additional-costs-table">
                    <thead>
                        <tr>
                            <th>Amount</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="additionalCostsTableBody"></tbody>
                </table>
            </div>
            
            <div style="text-align: center; margin-top: 35px;">
                <button type="button" class="btn" onclick="saveMonthChanges()">Save Basic Info</button>
                <button type="button" class="btn btn-secondary" onclick="closeEditModal()" style="margin-left: 15px;">Close</button>
            </div>
        </div>
    </div>

    <div id="addCostModal" class="form-modal">
        <div class="modal-content">
            <span class="close" onclick="closeAddCostModal()">&times;</span>
            <h2>Add Additional Cost</h2>
            <form id="addCostForm">
                <div class="form-group">
                    <label for="costAmount">Amount ($)</label>
                    <input type="number" id="costAmount" step="0.01" placeholder="50.00" required>
                </div>
                <div class="form-group">
                    <label for="costDescription">Description</label>
                    <input type="text" id="costDescription" placeholder="Grocery, Gas, etc." required>
                </div>
                <div style="text-align: center; margin-top: 35px;">
                    <button type="submit" class="btn">Add Cost</button>
                    <button type="button" class="btn btn-secondary" onclick="closeAddCostModal()" style="margin-left: 15px;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <div id="paymentModal" class="form-modal">
        <div class="modal-content">
            <span class="close" onclick="closePaymentModal()">&times;</span>
            <h2>Add Payment for <span id="paymentMonthName"></span></h2>
            <div id="currentPaymentSummary" style="margin-bottom: 25px; padding: 20px; background: #2d3748; border-radius: 12px;"></div>
            <form id="paymentForm">
                <div class="form-group">
                    <label for="paymentAmount">Payment Amount ($)</label>
                    <input type="number" id="paymentAmount" step="0.01" placeholder="500.00" required>
                </div>
                <div style="text-align: center; margin-top: 35px;">
                    <button type="submit" class="btn">Add Payment</button>
                    <button type="button" class="btn btn-secondary" onclick="closePaymentModal()" style="margin-left: 15px;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let budgetData = [];
        let currentEditingMonth = null;
        let currentPaymentMonth = null;

        function showMessage(msg, isError = false) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="message ${isError ? 'error' : 'success'}">${msg}</div>`;
            setTimeout(() => messageDiv.innerHTML = '', 3000);
        }

        function formatCurrency(amount) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2
            }).format(amount);
        }

        function openModal() {
            document.getElementById('monthModal').style.display = 'block';
            document.getElementById('monthName').focus();
        }

        function closeModal() {
            document.getElementById('monthModal').style.display = 'none';
            document.getElementById('monthForm').reset();
        }
        
        function closeEditModal() {
            document.getElementById('editModal').style.display = 'none';
            currentEditingMonth = null;
        }

        function openAddCostModal() {
            document.getElementById('addCostModal').style.display = 'block';
            document.getElementById('costAmount').value = '';
            document.getElementById('costDescription').value = '';
            document.getElementById('costAmount').focus();
        }

        function closeAddCostModal() {
            document.getElementById('addCostModal').style.display = 'none';
        }

        function openPaymentModal(monthName) {
            currentPaymentMonth = monthName;
            document.getElementById('paymentMonthName').textContent = monthName;
            document.getElementById('paymentModal').style.display = 'block';
            document.getElementById('paymentAmount').value = '';
            loadPaymentSummary(monthName);
            document.getElementById('paymentAmount').focus();
        }

        function closePaymentModal() {
            document.getElementById('paymentModal').style.display = 'none';
            currentPaymentMonth = null;
        }

        async function loadPaymentSummary(monthName) {
            try {
                const response = await fetch(`/api/months/${monthName}`);
                const month = await response.json();
                
                const totalPaid = month.payments ? month.payments.reduce((sum, p) => sum + p, 0) : 0;
                const owed = month.total_month_due - totalPaid;
                
                document.getElementById('currentPaymentSummary').innerHTML = `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Total Month Due:</span>
                        <span>${formatCurrency(month.total_month_due)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Total Paid:</span>
                        <span>${formatCurrency(totalPaid)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-weight: bold; color: ${owed > 0 ? '#fc8181' : '#68d391'};">
                        <span>Amount Owed:</span>
                        <span>${formatCurrency(owed)}</span>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading payment summary:', error);
            }
        }

        async function addPayment(monthName) {
            openPaymentModal(monthName);
        }

        window.onclick = function(event) {
            const modal = document.getElementById('monthModal');
            const editModal = document.getElementById('editModal');
            const addCostModal = document.getElementById('addCostModal');
            const paymentModal = document.getElementById('paymentModal');
            if (event.target === modal) closeModal();
            if (event.target === editModal) closeEditModal();
            if (event.target === addCostModal) closeAddCostModal();
            if (event.target === paymentModal) closePaymentModal();
        }

        async function loadMonths() {
            const loading = document.getElementById('loading');
            const table = document.getElementById('budgetTable');
            const emptyState = document.getElementById('emptyState');
            
            loading.style.display = 'block';
            table.style.display = 'none';
            emptyState.style.display = 'none';

            try {
                const response = await fetch('/api/months');
                if (!response.ok) throw new Error('Failed to load data');
                
                const months = await response.json();
                budgetData = months;

                if (months.length === 0) {
                    loading.style.display = 'none';
                    emptyState.style.display = 'block';
                    return;
                }

                const detailedMonths = await Promise.all(
                    months.map(async (month) => {
                        const detailResponse = await fetch(`/api/months/${month.month}`);
                        return await detailResponse.json();
                    })
                );

                renderSpreadsheet(detailedMonths);
                loading.style.display = 'none';
                table.style.display = 'table';

            } catch (error) {
                loading.style.display = 'none';
                showMessage('Error loading budget data: ' + error.message, true);
            }
        }

        function renderSpreadsheet(months) {
            const tbody = document.getElementById('budgetTableBody');
            
            months.sort((a, b) => b.month_name.localeCompare(a.month_name));
            
            tbody.innerHTML = months.map(month => {
                const totalPaid = month.payments ? month.payments.reduce((sum, payment) => sum + payment, 0) : 0;
                const owed = month.total_month_due - totalPaid;
                
                return `
                <tr>
                    <td class="month-cell" onclick="showMonthSummary('${month.month_name}')" title="Click to view detailed summary">${month.month_name}</td>
                    <td class="currency">${formatCurrency(month.rent)}</td>
                    <td class="currency">${formatCurrency(month.heating)}</td>
                    <td class="currency">${formatCurrency(month.electric)}</td>
                    <td class="currency">${formatCurrency(month.water)}</td>
                    <td class="currency">${formatCurrency(month.internet)}</td>
                    <td class="currency ${month.total_additional_costs > 0 ? 'negative' : ''}">${formatCurrency(month.total_additional_costs)}</td>
                    <td class="currency positive">${formatCurrency(month.total_utilities)}</td>
                    <td class="currency positive">${formatCurrency(month.utilities_per_roommate)}</td>
                    <td class="currency positive">${formatCurrency(month.total_housing)}</td>
                    <td class="currency total-row">${formatCurrency(month.total_month_due)}</td>
                    <td class="currency ${totalPaid > 0 ? 'positive' : ''}" onclick="addPayment('${month.month_name}')" style="cursor: pointer;" title="Click to add payment">${formatCurrency(totalPaid)}</td>
                    <td class="currency ${owed > 0 ? 'negative' : 'positive'}">${formatCurrency(owed)}</td>
                    <td class="actions-cell">
                        <button class="btn btn-small btn-info" onclick="editMonth('${month.month_name}')">Edit</button>
                    </td>
                </tr>
            `;
            }).join('');
        }

        async function showMonthSummary(monthName) {
            try {
                const response = await fetch(`/api/months/${monthName}`);
                if (!response.ok) throw new Error('Failed to load month details');
                
                const month = await response.json();
                
                document.getElementById('summaryTitle').textContent = `Month Summary: ${month.month_name}`;
                
                let additionalCostsHtml = '';
                if (month.additional_costs && month.additional_costs.length > 0) {
                    additionalCostsHtml = `
                        <table class="additional-costs-table">
                            <thead>
                                <tr>
                                    <th>Amount</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${month.additional_costs.map((cost, index) => `
                                    <tr>
                                        <td>${formatCurrency(cost.amount)}</td>
                                        <td>${cost.description}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                        <div class="cost-line">
                            <span>TOTAL ADDITIONAL COSTS:</span>
                            <span>${formatCurrency(month.total_additional_costs)}</span>
                        </div>
                    `;
                } else {
                    additionalCostsHtml = '<p style="color: #a0aec0; font-style: italic;">No additional costs stored</p>';
                }

                const summaryHtml = `
                    <div class="summary-section">
                        <h3>Fixed Monthly Costs</h3>
                        <div class="cost-line">
                            <span>Rent:</span>
                            <span>${formatCurrency(month.rent)}</span>
                        </div>
                        <div class="cost-line">
                            <span>Heating:</span>
                            <span>${formatCurrency(month.heating)}</span>
                        </div>
                        <div class="cost-line">
                            <span>Electric:</span>
                            <span>${formatCurrency(month.electric)}</span>
                        </div>
                        <div class="cost-line">
                            <span>Water:</span>
                            <span>${formatCurrency(month.water)}</span>
                        </div>
                        <div class="cost-line">
                            <span>Internet:</span>
                            <span>${formatCurrency(month.internet)}</span>
                        </div>
                        <div class="cost-line">
                            <span>Total Utilities:</span>
                            <span>${formatCurrency(month.total_utilities)}</span>
                        </div>
                        <div class="cost-line">
                            <span>Your Utilities Share: </span>
                            <span>${formatCurrency(month.utilities_per_roommate)}</span>
                        </div>
                    </div>

                    <div class="summary-section">
                        <h3>Total Housing</h3>
                        <div class="cost-line">
                            <span>TOTAL HOUSING:</span>
                            <span>${formatCurrency(month.total_housing)}</span>
                        </div>
                    </div>

                    <div class="summary-section">
                        <h3>Additional Costs</h3>
                        ${additionalCostsHtml}
                    </div>

                    <div class="summary-section">
                        <h3>Payments</h3>
                        ${month.payments && month.payments.length > 0 ? `
                            <table class="additional-costs-table">
                                <thead>
                                    <tr>
                                        <th>Payment #</th>
                                        <th>Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${month.payments.map((payment, index) => `
                                        <tr>
                                            <td>Payment ${index + 1}</td>
                                            <td>${formatCurrency(payment)}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                            <div class="cost-line">
                                <span>TOTAL PAID:</span>
                                <span>${formatCurrency(month.payments.reduce((sum, p) => sum + p, 0))}</span>
                            </div>
                        ` : '<p style="color: #a0aec0; font-style: italic;">No payments recorded</p>'}
                    </div>

                    <div class="grand-total">
                        TOTAL MONTH DUE: ${formatCurrency(month.total_month_due)}
                    </div>
                    
                    <div class="grand-total" style="background: linear-gradient(135deg, ${(month.total_month_due - (month.payments ? month.payments.reduce((sum, p) => sum + p, 0) : 0)) > 0 ? '#e53e3e, #c53030' : '#2f855a, #38a169'});">
                        AMOUNT OWED: ${formatCurrency(month.total_month_due - (month.payments ? month.payments.reduce((sum, p) => sum + p, 0) : 0))}
                    </div>
                `;

                document.getElementById('summaryBody').innerHTML = summaryHtml;
                document.getElementById('summaryModal').style.display = 'block';

            } catch (error) {
                showMessage('Error loading month summary: ' + error.message, true);
            }
        }

        function closeSummaryModal() {
            document.getElementById('summaryModal').style.display = 'none';
        }

        async function createMonth(event) {
            event.preventDefault();
            
            const data = {
                month_name: document.getElementById('monthName').value,
                rent: parseFloat(document.getElementById('rent').value) || 0,
                heating: parseFloat(document.getElementById('heating').value) || 0,
                electric: parseFloat(document.getElementById('electric').value) || 0,
                water: parseFloat(document.getElementById('water').value) || 0,
                internet: parseFloat(document.getElementById('internet').value) || 0
            };

            try {
                const response = await fetch('/api/months', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    showMessage(`Month ${data.month_name} created successfully!`);
                    closeModal();
                    loadMonths();
                } else {
                    const error = await response.json();
                    showMessage(error.error || 'Error creating month', true);
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, true);
            }
        }
        
        async function editMonth(monthName) {
            try {
                const response = await fetch(`/api/months/${monthName}`);
                if (!response.ok) {
                    throw new Error('Failed to load month data');
                }
                
                const monthData = await response.json();
                currentEditingMonth = monthName;
                
                document.getElementById('editMonthName').textContent = monthName;
                document.getElementById('editRent').value = monthData.rent;
                document.getElementById('editHeating').value = monthData.heating;
                document.getElementById('editElectric').value = monthData.electric;
                document.getElementById('editWater').value = monthData.water;
                document.getElementById('editInternet').value = monthData.internet;
                
                renderAdditionalCostsTable(monthData.additional_costs || []);
                
                document.getElementById('editModal').style.display = 'block';
                
            } catch (error) {
                showMessage('Error loading month data: ' + error.message, true);
            }
        }
        
        function renderAdditionalCostsTable(additionalCosts) {
            const tbody = document.getElementById('additionalCostsTableBody');
            
            if (additionalCosts.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #a0aec0; font-style: italic;">No additional costs yet</td></tr>';
                return;
            }
            
            tbody.innerHTML = additionalCosts.map((cost, index) => `
                <tr>
                    <td class="currency">${formatCurrency(cost.amount)}</td>
                    <td>${cost.description}</td>
                    <td class="actions-cell">
                        <button class="btn btn-small btn-secondary" onclick="editAdditionalCost(${index})">Edit</button>
                        <button class="btn btn-small btn-danger" onclick="deleteAdditionalCost(${index})">Delete</button>
                    </td>
                </tr>
            `).join('');
            
            const total = additionalCosts.reduce((sum, cost) => sum + (parseFloat(cost.amount) || 0), 0);
            tbody.innerHTML += `
                <tr class="total-row">
                    <td class="currency"><strong>${formatCurrency(total)}</strong></td>
                    <td><strong>Total</strong></td>
                    <td></td>
                </tr>
            `;
        }

        async function editAdditionalCost(index) {
            if (!currentEditingMonth) return;
            
            const monthData = await fetch(`/api/months/${currentEditingMonth}`).then(r => r.json());
            const cost = monthData.additional_costs[index];
            
            const newAmount = prompt('Enter new amount:', cost.amount);
            if (newAmount === null) return;
            
            const newDescription = prompt('Enter new description:', cost.description);
            if (newDescription === null) return;
            
            const amount = parseFloat(newAmount);
            if (isNaN(amount) || amount <= 0) {
                showMessage('Please enter a valid amount', true);
                return;
            }
            
            if (!newDescription.trim()) {
                showMessage('Description cannot be empty', true);
                return;
            }
            
            try {
                const response = await fetch(`/api/months/${currentEditingMonth}/additional-costs/${index}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount, description: newDescription.trim() })
                });

                if (response.ok) {
                    showMessage('Additional cost updated successfully!');
                    await loadMonths();
                    editMonth(currentEditingMonth);
                } else {
                    const error = await response.json();
                    showMessage(error.error || 'Error updating cost', true);
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, true);
            }
        }

        async function saveMonthChanges() {
            if (!currentEditingMonth) return;
            
            const data = {
                rent: parseFloat(document.getElementById('editRent').value) || 0,
                heating: parseFloat(document.getElementById('editHeating').value) || 0,
                electric: parseFloat(document.getElementById('editElectric').value) || 0,
                water: parseFloat(document.getElementById('editWater').value) || 0,
                internet: parseFloat(document.getElementById('editInternet').value) || 0
            };

            try {
                const response = await fetch(`/api/months/${currentEditingMonth}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    showMessage(`Month ${currentEditingMonth} updated successfully!`);
                    closeEditModal();
                    loadMonths();
                } else {
                    const error = await response.json();
                    showMessage(error.error || 'Error updating month', true);
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, true);
            }
        }

        async function addAdditionalCost(event) {
            event.preventDefault();
            
            if (!currentEditingMonth) return;
            
            const amount = parseFloat(document.getElementById('costAmount').value);
            const description = document.getElementById('costDescription').value.trim();
            
            if (!amount || !description) {
                showMessage('Please fill in both amount and description', true);
                return;
            }
            
            try {
                const response = await fetch(`/api/months/${currentEditingMonth}/additional-costs`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount, description })
                });

                if (response.ok) {
                    showMessage('Additional cost added successfully!');
                    closeAddCostModal();
                    const updatedMonth = await fetch(`/api/months/${currentEditingMonth}`).then(r => r.json());
                    renderAdditionalCostsTable(updatedMonth.additional_costs || []);
                    await loadMonths();
                } else {
                    const error = await response.json();
                    showMessage(error.error || 'Error adding cost', true);
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, true);
            }
        }

        async function deleteAdditionalCost(index) {
            if (!currentEditingMonth) return;
            
            if (!confirm('Are you sure you want to delete this additional cost?')) return;
            
            try {
                const response = await fetch(`/api/months/${currentEditingMonth}/additional-costs/${index}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    showMessage('Additional cost deleted successfully!');
                    const updatedMonth = await fetch(`/api/months/${currentEditingMonth}`).then(r => r.json());
                    renderAdditionalCostsTable(updatedMonth.additional_costs || []);
                    await loadMonths();
                } else {
                    const error = await response.json();
                    showMessage(error.error || 'Error deleting cost', true);
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, true);
            }
        }

        async function addPaymentSubmit(event) {
            event.preventDefault();
            
            if (!currentPaymentMonth) return;
            
            const amount = parseFloat(document.getElementById('paymentAmount').value);
            
            if (!amount || amount <= 0) {
                showMessage('Please enter a valid payment amount', true);
                return;
            }
            
            try {
                const response = await fetch(`/api/months/${currentPaymentMonth}/payments`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount })
                });

                if (response.ok) {
                    showMessage(`Payment of ${formatCurrency(amount)} added successfully!`);
                    closePaymentModal();
                    await loadMonths();
                } else {
                    const error = await response.json();
                    showMessage(error.error || 'Error adding payment', true);
                }
            } catch (error) {
                showMessage('Network error: ' + error.message, true);
            }
        }

        function exportData() {
            if (budgetData.length === 0) {
                showMessage('No data to export', true);
                return;
            }

            const csvContent = "data:text/csv;charset=utf-8," 
                + "Month,Total Due\\n"
                + budgetData.map(row => `${row.month},${row.total}`).join("\\n");

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "budget_tracker.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showMessage('Data exported successfully!');
        }

        document.getElementById('monthForm').addEventListener('submit', createMonth);
        document.getElementById('addCostForm').addEventListener('submit', addAdditionalCost);
        document.getElementById('paymentForm').addEventListener('submit', addPaymentSubmit);
        
        document.addEventListener('DOMContentLoaded', function() {
            loadMonths();
        });

        window.addEventListener('click', function(event) {
            const summaryModal = document.getElementById('summaryModal');
            const monthModal = document.getElementById('monthModal');
            const editModal = document.getElementById('editModal');
            const addCostModal = document.getElementById('addCostModal');
            const paymentModal = document.getElementById('paymentModal');
            
            if (event.target === summaryModal) {
                closeSummaryModal();
            }
            if (event.target === monthModal) {
                closeModal();
            }
            if (event.target === editModal) {
                closeEditModal();
            }
            if (event.target === addCostModal) {
                closeAddCostModal();
            }
            if (event.target === paymentModal) {
                closePaymentModal();
            }
        });
    </script>
</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/months', methods=['GET'])
def get_all_months():
    try:
        months_dict = load_data()
        result = []
        for month_name, month_obj in months_dict.items():
            result.append({
                'month': month_name,
                'total': month_obj.calculate_total_month_due()
            })
        result.sort(key=lambda x: x['month'], reverse=True)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/months/<month_name>', methods=['GET'])
def get_month(month_name):
    try:
        months_dict = load_data()
        if month_name not in months_dict:
            return jsonify({'error': 'Month not found'}), 404
        month_obj = months_dict[month_name]
        return jsonify(month_obj.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/months', methods=['POST'])
def create_month():
    try:
        data = request.get_json()
        months_dict = load_data()
        
        month_name = data['month_name']
        
        try:
            datetime.datetime.strptime(month_name, "%Y-%m")
        except ValueError:
            return jsonify({'error': 'Invalid month format. Use YYYY-MM'}), 400
        
        if month_name in months_dict:
            return jsonify({'error': f'Month {month_name} already exists'}), 400
        
        new_month = Month(
            month_name,
            float(data.get('rent', 0)),
            float(data.get('heating', 0)),
            float(data.get('electric', 0)),
            float(data.get('water', 0)),
            float(data.get('internet', 0)),
            [],
            []
        )
        
        months_dict[month_name] = new_month
        save_data(months_dict)
        
        return jsonify(new_month.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/months/<month_name>', methods=['PUT'])
def update_month(month_name):
    try:
        data = request.get_json()
        months_dict = load_data()
        
        if month_name not in months_dict:
            return jsonify({'error': 'Month not found'}), 404
        
        month_obj = months_dict[month_name]
        
        if 'rent' in data:
            month_obj.rent = float(data['rent'])
        if 'heating' in data:
            month_obj.heating = float(data['heating'])
        if 'electric' in data:
            month_obj.electric = float(data['electric'])
        if 'water' in data:
            month_obj.water = float(data['water'])
        if 'internet' in data:
            month_obj.internet = float(data['internet'])
        
        save_data(months_dict)
        return jsonify(month_obj.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/months/<month_name>/additional-costs', methods=['POST'])
def add_additional_cost(month_name):
    try:
        data = request.get_json()
        months_dict = load_data()
        
        if month_name not in months_dict:
            return jsonify({'error': 'Month not found'}), 404
        
        month_obj = months_dict[month_name]
        amount = float(data.get('amount', 0))
        description = data.get('description', '').strip()
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        month_obj.add_additional_cost(amount, description)
        save_data(months_dict)
        
        return jsonify(month_obj.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/months/<month_name>/additional-costs/<int:cost_index>', methods=['PUT'])
def update_additional_cost(month_name, cost_index):
    try:
        data = request.get_json()
        months_dict = load_data()
        
        if month_name not in months_dict:
            return jsonify({'error': 'Month not found'}), 404
        
        month_obj = months_dict[month_name]
        
        if cost_index < 0 or cost_index >= len(month_obj.additional_costs):
            return jsonify({'error': 'Invalid cost index'}), 400
        
        amount = float(data.get('amount', 0))
        description = data.get('description', '').strip()
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        month_obj.additional_costs[cost_index] = {
            'amount': amount,
            'description': description
        }
        
        save_data(months_dict)
        
        return jsonify({
            'message': f'Updated cost: ${amount:.2f} - {description}',
            'updated_month': month_obj.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/months/<month_name>/additional-costs/<int:cost_index>', methods=['DELETE'])
def delete_additional_cost(month_name, cost_index):
    try:
        months_dict = load_data()
        
        if month_name not in months_dict:
            return jsonify({'error': 'Month not found'}), 404
        
        month_obj = months_dict[month_name]
        
        if cost_index < 0 or cost_index >= len(month_obj.additional_costs):
            return jsonify({'error': 'Invalid cost index'}), 400
        
        deleted_cost = month_obj.additional_costs.pop(cost_index)
        save_data(months_dict)
        
        return jsonify({
            'message': f'Deleted cost: ${deleted_cost["amount"]:.2f} - {deleted_cost["description"]}',
            'updated_month': month_obj.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/months/<month_name>/payments', methods=['POST'])
def add_payment(month_name):
    try:
        data = request.get_json()
        months_dict = load_data()
        
        if month_name not in months_dict:
            return jsonify({'error': 'Month not found'}), 404
        
        month_obj = months_dict[month_name]
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'error': 'Payment amount must be greater than 0'}), 400
        
        month_obj.add_payment(amount)
        save_data(months_dict)
        
        return jsonify(month_obj.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Budget Tracker Web App...")
    print("Open your browser to: http://localhost:5000")
    print("Your CLI data will be used automatically!")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)