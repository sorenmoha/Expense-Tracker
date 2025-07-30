# web_app.py - Complete Flask app with beautiful spreadsheet frontend

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import datetime

# Import your existing modules
from month import Month
from utils import load_data, save_data

app = Flask(__name__)
CORS(app)

# Complete HTML template with spreadsheet styling
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Budget Tracker - Spreadsheet View</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f8f9fa;
            color: #212529;
            font-size: 16px;
            line-height: 1.5;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 { 
            font-size: 2.5rem; 
            margin-bottom: 10px; 
            font-weight: 700;
        }
        .header p { 
            font-size: 1.2rem; 
            opacity: 0.95; 
            font-weight: 400;
        }

        .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px; }

        .actions-bar {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }

        .btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            min-height: 48px;
        }

        .btn:hover {
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        }

        .btn-danger { background: #f44336; }
        .btn-danger:hover { background: #da190b; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #5a6268; }
        .btn-small { 
            padding: 8px 16px; 
            font-size: 14px; 
            margin: 0 4px;
            min-height: 36px;
        }

        .spreadsheet-container {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }

        .spreadsheet-table {
            width: 100%;
            border-collapse: collapse;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-size: 15px;
        }

        .spreadsheet-table th {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            color: #495057;
            padding: 16px 14px;
            text-align: left;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #dee2e6;
            border-right: 1px solid #dee2e6;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .spreadsheet-table td {
            padding: 14px 12px;
            border-bottom: 1px solid #e9ecef;
            border-right: 1px solid #e9ecef;
            font-size: 15px;
            white-space: nowrap;
        }

        .spreadsheet-table tbody tr:hover { background: #f8f9fa; }
        .spreadsheet-table tbody tr:nth-child(even) { background: #fdfdfd; }
        .month-cell { font-weight: 600; color: #495057; background: #e3f2fd !important; }
        .currency { text-align: right; font-family: 'Courier New', monospace; font-weight: 500; }
        .currency.positive { color: #28a745; }
        .currency.negative { color: #dc3545; }
        .total-row { background: #fff3cd !important; font-weight: 700; }
        .actions-cell { text-align: center; }

        .month-cell:hover {
            background: #bbdefb !important;
            cursor: pointer;
            text-decoration: underline;
        }

        .summary-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }

        .summary-content {
            background: white;
            margin: 2% auto;
            padding: 0;
            border-radius: 15px;
            width: 90%;
            max-width: 800px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: modalSlideIn 0.3s ease;
            max-height: 90vh;
            overflow-y: auto;
        }

        .summary-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px 15px 0 0;
            text-align: center;
        }

        .summary-body {
            padding: 30px;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            line-height: 1.6;
            font-size: 16px;
        }

        .summary-section {
            margin-bottom: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .summary-section h3 {
            color: #495057;
            margin-bottom: 15px;
            font-family: 'Segoe UI', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 14px;
        }

        .cost-line {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px dotted #dee2e6;
        }

        .cost-line:last-child {
            border-bottom: none;
            font-weight: bold;
            margin-top: 10px;
            padding-top: 15px;
            border-top: 2px solid #667eea;
        }

        .additional-costs-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }

        .additional-costs-table th {
            background: #e9ecef;
            padding: 10px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #dee2e6;
        }

        .additional-costs-table td {
            padding: 10px;
            border: 1px solid #dee2e6;
        }

        .grand-total {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            margin-top: 20px;
        }

        .console-container {
            background: #1e1e1e;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            font-family: -apple-system, BlinkMacSystemFont, 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            color: #d4d4d4;
            border: 1px solid #333;
        }

        .console-header {
            background: #2d2d30;
            padding: 12px 20px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #333;
        }

        .console-header h3 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
            color: #d4d4d4;
        }

        .console-close {
            background: none;
            border: none;
            color: #d4d4d4;
            font-size: 18px;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
        }

        .console-close:hover {
            background: #404040;
        }

        .console-output {
            height: 300px;
            overflow-y: auto;
            padding: 16px 20px;
            font-size: 14px;
            line-height: 1.4;
            background: #1e1e1e;
        }

        .console-line {
            margin-bottom: 4px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .console-line.command {
            color: #569cd6;
        }

        .console-line.success {
            color: #4ec9b0;
        }

        .console-line.error {
            color: #f44747;
        }

        .console-line.info {
            color: #dcdcaa;
        }

        .console-input-container {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            background: #2d2d30;
            border-radius: 0 0 12px 12px;
            border-top: 1px solid #333;
        }

        .console-prompt {
            color: #4ec9b0;
            font-weight: 600;
            margin-right: 8px;
            font-size: 14px;
        }

        .console-input {
            flex: 1;
            background: transparent;
            border: none;
            color: #d4d4d4;
            font-family: inherit;
            font-size: 14px;
            outline: none;
        }

        .console-input::placeholder {
            color: #6a6a6a;
        }

        .message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

        .form-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
        }

        .modal-content {
            background: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }

        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-weight: 600; margin-bottom: 8px; color: #495057; }
        .form-group input {
            padding: 14px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
        }
        .close:hover { color: #333; }

        .loading { text-align: center; padding: 40px; color: #6c757d; }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        .empty-state { text-align: center; padding: 60px 20px; color: #6c757d; }
        .empty-state h3 { margin-bottom: 10px; color: #495057; }

        @media (max-width: 768px) {
            .container {
                padding: 20px 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .header p {
                font-size: 1rem;
            }
            
            .actions-bar {
                flex-direction: column;
                align-items: stretch;
                gap: 10px;
            }
            
            .console-container {
                margin-bottom: 20px;
            }
            
            .console-output {
                height: 200px;
                padding: 12px 16px;
                font-size: 13px;
            }
            
            .console-input-container {
                padding: 10px 16px;
            }
            
            .console-prompt,
            .console-input {
                font-size: 13px;
            }
            
            .btn {
                width: 100%;
                justify-content: center;
                padding: 16px 20px;
                font-size: 16px;
            }
            
            .spreadsheet-container {
                overflow-x: auto;
                border-radius: 8px;
                -webkit-overflow-scrolling: touch;
            }
            
            .spreadsheet-table {
                min-width: 1000px;
                font-size: 14px;
            }
            
            .spreadsheet-table th {
                padding: 12px 8px;
                font-size: 12px;
                white-space: nowrap;
            }
            
            .spreadsheet-table td {
                padding: 12px 8px;
                font-size: 14px;
            }
            
            .currency {
                font-size: 14px;
            }
            
            .month-cell {
                font-size: 14px;
                min-width: 80px;
            }
            
            .btn-small {
                padding: 8px 12px;
                font-size: 13px;
                white-space: nowrap;
            }
            
            .form-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .modal-content {
                margin: 10% auto;
                padding: 20px;
                width: 95%;
            }
            
            .summary-content {
                margin: 5% auto;
                width: 95%;
                max-height: 85vh;
            }
            
            .summary-body {
                padding: 20px;
                font-size: 15px;
            }
            
            .additional-costs-table {
                font-size: 14px;
            }
            
            .additional-costs-table th,
            .additional-costs-table td {
                padding: 8px 6px;
            }
        }

        @media (max-width: 480px) {
            .spreadsheet-table {
                font-size: 13px;
            }
            
            .spreadsheet-table th {
                padding: 10px 6px;
                font-size: 11px;
            }
            
            .spreadsheet-table td {
                padding: 10px 6px;
                font-size: 13px;
            }
            
            .currency {
                font-size: 13px;
            }
            
            .btn-small {
                padding: 6px 10px;
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>expense tracker</h1>
    </div>

    <div class="container">
        <div class="actions-bar">
            <button class="btn" onclick="openModal()">Add New Month</button>
            <button class="btn btn-secondary" onclick="loadMonths()">Refresh Data</button>
            <button class="btn btn-secondary" onclick="exportData()">Export CSV</button>
            <button class="btn btn-secondary" onclick="toggleConsole()">Toggle Console</button>
        </div>

        <div id="console-container" class="console-container" style="display: none;">
            <div class="console-header">
                <h3>CLI Console</h3>
                <button class="console-close" onclick="toggleConsole()">&times;</button>
            </div>
            <div class="console-output" id="consoleOutput">
                <div class="console-line">Budget Tracker CLI Console - Type 'help' for available commands</div>
            </div>
            <div class="console-input-container">
                <span class="console-prompt">tracker$ </span>
                <input type="text" id="consoleInput" class="console-input" placeholder="Enter CLI command..." autocomplete="off">
            </div>
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
                        <th>Additional Costs</th>
                        <th>Total Utilities</th>
                        <th>Your Share</th>
                        <th>Housing Total</th>
                        <th>Additional Costs</th>
                        <th>Monthly Total</th>
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

    <!-- Modal for month summary -->
    <div id="summaryModal" class="summary-modal">
        <div class="summary-content">
            <div class="summary-header">
                <span class="close" onclick="closeSummaryModal()" style="float: right; font-size: 24px; cursor: pointer;">&times;</span>
                <h2 id="summaryTitle">Month Summary</h2>
            </div>
            <div class="summary-body" id="summaryBody">
                <!-- Summary content will be populated here -->
            </div>
        </div>
    </div>

    <!-- Modal for adding new month -->
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
                <div style="text-align: center; margin-top: 30px;">
                    <button type="submit" class="btn">Create Month</button>
                    <button type="button" class="btn btn-secondary" onclick="closeModal()" style="margin-left: 10px;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let budgetData = [];
        let consoleHistory = [];
        let historyIndex = -1;

        function toggleConsole() {
            const console = document.getElementById('console-container');
            const isVisible = console.style.display !== 'none';
            console.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                document.getElementById('consoleInput').focus();
            }
        }

        function addConsoleOutput(text, type = 'info') {
            const output = document.getElementById('consoleOutput');
            const line = document.createElement('div');
            line.className = `console-line ${type}`;
            line.textContent = text;
            output.appendChild(line);
            output.scrollTop = output.scrollHeight;
        }

        async function executeCliCommand(command) {
            if (!command.trim()) return;
            
            // Add command to history
            consoleHistory.unshift(command);
            historyIndex = -1;
            
            // Display the command
            addConsoleOutput(`tracker$ ${command}`, 'command');
            
            try {
                const response = await fetch('/api/cli', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command.trim() })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Handle successful command
                    if (result.output) {
                        result.output.split('\\n').forEach(line => {
                            if (line.trim()) {
                                addConsoleOutput(line, result.success ? 'success' : 'info');
                            }
                        });
                    }
                    
                    // Refresh data if command modified anything
                    if (result.refresh_needed) {
                        loadMonths();
                    }
                } else {
                    addConsoleOutput(`Error: ${result.error}`, 'error');
                }
            } catch (error) {
                addConsoleOutput(`Network error: ${error.message}`, 'error');
            }
        }

        function showMessage(text, isError = false) {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="message ${isError ? 'error' : 'success'}">${text}</div>`;
            setTimeout(() => messageDiv.innerHTML = '', 5000);
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

        window.onclick = function(event) {
            const modal = document.getElementById('monthModal');
            if (event.target === modal) closeModal();
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
            
            tbody.innerHTML = months.map(month => `
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
                    <td class="actions-cell">
                        <button class="btn btn-small btn-danger" onclick="deleteMonth('${month.month_name}')">Delete</button>
                    </td>
                </tr>
            `).join('');
        }

        function calculateTotals(months) {
            return months.reduce((totals, month) => ({
                rent: totals.rent + month.rent,
                heating: totals.heating + month.heating,
                electric: totals.electric + month.electric,
                water: totals.water + month.water,
                internet: totals.internet + month.internet,
                total_utilities: totals.total_utilities + month.total_utilities,
                utilities_per_roommate: totals.utilities_per_roommate + month.utilities_per_roommate,
                total_housing: totals.total_housing + month.total_housing,
                total_additional_costs: totals.total_additional_costs + month.total_additional_costs,
                total_month_due: totals.total_month_due + month.total_month_due
            }), {
                rent: 0, heating: 0, electric: 0, water: 0, internet: 0,
                total_utilities: 0, utilities_per_roommate: 0, total_housing: 0,
                total_additional_costs: 0, total_month_due: 0
            });
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
                                    <th>#</th>
                                    <th>Amount</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${month.additional_costs.map((cost, index) => `
                                    <tr>
                                        <td>${index + 1}</td>
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
                    additionalCostsHtml = '<p style="color: #6c757d; font-style: italic;">No additional costs stored</p>';
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

                    <div class="grand-total">
                        TOTAL MONTH DUE: ${formatCurrency(month.total_month_due)}
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

        async function deleteMonth(monthName) {
            if (!confirm(`Are you sure you want to delete ${monthName}?\\n\\nThis action cannot be undone.`)) return;

            try {
                const response = await fetch(`/api/months/${monthName}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    showMessage(`Month ${monthName} deleted successfully!`);
                    loadMonths();
                } else {
                    const error = await response.json();
                    showMessage(error.error || 'Error deleting month', true);
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
        document.addEventListener('DOMContentLoaded', loadMonths);
        
        // Console input handling
        document.getElementById('consoleInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const command = this.value;
                this.value = '';
                executeCliCommand(command);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (historyIndex < consoleHistory.length - 1) {
                    historyIndex++;
                    this.value = consoleHistory[historyIndex] || '';
                }
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    this.value = consoleHistory[historyIndex] || '';
                } else if (historyIndex === 0) {
                    historyIndex = -1;
                    this.value = '';
                }
            }
        });
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
                closeSummaryModal();
            }
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                openModal();
            }
            if (e.ctrlKey && e.key === '`') {
                e.preventDefault();
                toggleConsole();
            }
        });

        // Close summary modal when clicking outside
        window.addEventListener('click', function(event) {
            const summaryModal = document.getElementById('summaryModal');
            const monthModal = document.getElementById('monthModal');
            if (event.target === summaryModal) {
                closeSummaryModal();
            }
            if (event.target === monthModal) {
                closeModal();
            }
        });
    </script>
</body>
</html>'''

# Routes - same as before but serving the new template

@app.route('/')
def home():
    """Serve the beautiful spreadsheet interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/months', methods=['GET'])
def get_all_months():
    """Same as: tracker -l"""
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
    """Same as: tracker -l YYYY-MM"""
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
    """Same as: tracker -n YYYY-MM"""
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
            []
        )
        
        months_dict[month_name] = new_month
        save_data(months_dict)
        
        return jsonify(new_month.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/months/<month_name>', methods=['DELETE'])
def delete_month_route(month_name):
    """Same as: tracker -d YYYY-MM"""
    try:
        months_dict = load_data()
        if month_name not in months_dict:
            return jsonify({'error': 'Month not found'}), 404
        
        del months_dict[month_name]
        save_data(months_dict)
        return jsonify({'message': f'Month {month_name} deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cli', methods=['POST'])
def execute_cli_command():
    """Execute CLI commands via web interface"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Parse the command (simplified CLI parser)
        parts = command.split()
        
        if not parts:
            return jsonify({'error': 'Empty command'}), 400
        
        # Handle help command
        if parts[0] == 'help':
            help_text = """Available CLI commands:
-l, --list                    List all months
-l YYYY-MM                   Show specific month summary  
-n YYYY-MM                   Create new month (interactive)
-d YYYY-MM                   Delete month
-e YYYY-MM -t UTILITY        Edit utility (rent, heating, electric, water, internet)

Examples:
tracker -l                   # List all months
tracker -l 2025-01           # Show January 2025 summary
tracker -n 2025-02           # Create February 2025 (will prompt for values)
tracker -d 2025-01           # Delete January 2025
tracker -e 2025-01 -t rent   # Edit rent for January 2025"""
            return jsonify({'output': help_text, 'success': True, 'refresh_needed': False})
        
        # Handle list commands
        if parts[0] in ['-l', '--list']:
            months_dict = load_data()
            
            if len(parts) == 1:
                # List all months
                if not months_dict:
                    return jsonify({'output': 'No months have been added yet', 'success': True, 'refresh_needed': False})
                
                output = "Listing all months...\\n"
                for date, month_obj in months_dict.items():
                    total = month_obj.calculate_total_month_due()
                    output += f"  {date}: ${total:.2f}\\n"
                
                return jsonify({'output': output, 'success': True, 'refresh_needed': False})
            
            elif len(parts) == 2:
                # Show specific month
                month_name = parts[1]
                if month_name not in months_dict:
                    return jsonify({'error': f'No month found for {month_name}'}, 404)
                
                month_obj = months_dict[month_name]
                
                # Generate summary output (similar to display_summary)
                output = f"MONTH SUMMARY: {month_obj.month_name}\\n"
                output += "=" * 50 + "\\n\\n"
                output += "FIXED MONTHLY COSTS:\\n"
                output += f"   Rent:                ${month_obj.rent:.2f}\\n"
                output += f"   Heating:             ${month_obj.heating:.2f}\\n"
                output += f"   Electric:            ${month_obj.electric:.2f}\\n"
                output += f"   Water:               ${month_obj.water:.2f}\\n"
                output += f"   Internet:            ${month_obj.internet:.2f}\\n"
                output += "-" * 35 + "\\n"
                output += f"   Total Utilities:     ${month_obj.calculate_total_utilities():.2f}\\n"
                output += f"   Your Utilities Share: ${month_obj.calculate_utilities_per_roommate():.2f}\\n\\n"
                output += f"TOTAL HOUSING:       ${month_obj.calculate_total_housing_month_due():.2f}\\n\\n"
                
                # Additional costs
                if month_obj.additional_costs:
                    output += "ADDITIONAL COSTS:\\n"
                    for i, cost in enumerate(month_obj.additional_costs, 1):
                        output += f"   {i}. ${cost['amount']:.2f} - {cost['description']}\\n"
                    output += f"   TOTAL: ${month_obj.calculate_total_additional_costs():.2f}\\n\\n"
                else:
                    output += "ADDITIONAL COSTS: None\\n\\n"
                
                output += "=" * 50 + "\\n"
                output += f"TOTAL MONTH DUE:     ${month_obj.calculate_total_month_due():.2f}\\n"
                output += "=" * 50
                
                return jsonify({'output': output, 'success': True, 'refresh_needed': False})
        
        # Handle delete command
        elif parts[0] in ['-d', '--delete-month']:
            if len(parts) != 2:
                return jsonify({'error': 'Delete command requires month (YYYY-MM)'}, 400)
            
            month_name = parts[1]
            months_dict = load_data()
            
            if month_name not in months_dict:
                return jsonify({'error': f'No month found for {month_name}'}, 404)
            
            del months_dict[month_name]
            save_data(months_dict)
            
            return jsonify({
                'output': f'Deleted {month_name}',
                'success': True,
                'refresh_needed': True
            })
        
        # Handle new month creation (simplified - no interactive prompts)
        elif parts[0] in ['-n', '--new-entry']:
            return jsonify({
                'output': 'Use the "Add New Month" button above for creating new months via the web interface.',
                'success': True,
                'refresh_needed': False
            })
        
        # Handle edit command (simplified)
        elif parts[0] in ['-e', '--edit-month']:
            return jsonify({
                'output': 'Editing via CLI console is not yet implemented. Use the web interface or your original CLI.',
                'success': True,
                'refresh_needed': False
            })
        
        else:
            return jsonify({'error': f'Unknown command: {parts[0]}. Type "help" for available commands.'}, 400)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Budget Tracker Web App...")
    print("Open your browser to: http://localhost:5000")
    print("Your CLI data will be used automatically!")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)