from flask import Flask, jsonify, render_template_string, request, send_file
import qrcode
import io
import base64
from datetime import datetime

app = Flask(__name__)

# Store generated QR codes in memory (for demo purposes)
qr_history = []

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code Generator - DevOps Pipeline</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #27ae60;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #333;
            font-weight: bold;
            margin-bottom: 8px;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        .btn {
            background: #667eea;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .btn-download {
            background: #28a745;
            margin-top: 15px;
        }
        .btn-download:hover {
            background: #218838;
        }
        .qr-result {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .qr-result.active {
            display: block;
        }
        .qr-result img {
            max-width: 300px;
            border: 3px solid #667eea;
            border-radius: 10px;
            padding: 10px;
            background: white;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-box {
            background: #f8f9ff;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .stat-value {
            color: #667eea;
            font-size: 1.5em;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 20px;
        }
        .footer a {
            color: white;
            text-decoration: none;
            margin: 0 10px;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 QR Code Generator v2.0 - AUTOMATED!!</h1>
            <p>Create QR codes instantly | Deployed via DevOps Pipeline</p>
        </div>

        <div class="card">
            <div class="alert alert-info">
                <strong>ℹ️ How to use:</strong> Enter any text or URL below and click "Generate QR Code"
            </div>

            <form id="qrForm">
                <div class="form-group">
                    <label for="qrText">Enter Text or URL:</label>
                    <textarea 
                        id="qrText" 
                        name="text" 
                        placeholder="e.g., https://github.com/aquib20020/devops-pipeline-project"
                        required
                    ></textarea>
                </div>
                <button type="submit" class="btn">🎯 Generate QR Code</button>
            </form>

            <div id="qrResult" class="qr-result">
                <h2 style="color: #667eea; margin-bottom: 20px;">✅ QR Code Generated!</h2>
                <img id="qrImage" src="" alt="QR Code">
                <p style="margin-top: 15px; color: #666;">Scan this QR code with your phone camera</p>
                <button id="downloadBtn" class="btn btn-download">⬇️ Download QR Code</button>
            </div>
        </div>

        <div class="card">
            <h2 style="color: #667eea; margin-bottom: 20px;">📊 Statistics</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-label">QR Codes Generated</div>
                    <div class="stat-value" id="qrCount">{{ qr_count }}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Server Status</div>
                    <div class="stat-value">Live</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🚀 Deployed on AWS EC2 | Monitored with CloudWatch</p>
            <p>
                <a href="/health">Health Check</a> | 
                <a href="/stats">Statistics</a> | 
                <a href="https://github.com/aquib20020/devops-pipeline-project" target="_blank">GitHub</a>
            </p>
            <p style="margin-top: 10px;">⏰ {{ current_time }}</p>
        </div>
    </div>

    <script>
        let currentQRData = null;

        // Handle form submission
        document.getElementById('qrForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const text = document.getElementById('qrText').value;
            const resultDiv = document.getElementById('qrResult');
            const qrImage = document.getElementById('qrImage');
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text })
                });
                
                const data = await response.json();
                
                if (data.qr_code) {
                    currentQRData = data.qr_code;
                    qrImage.src = 'data:image/png;base64,' + data.qr_code;
                    resultDiv.classList.add('active');
                    document.getElementById('qrCount').textContent = data.total_generated;
                    
                    // Scroll to result
                    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } catch (error) {
                alert('Error generating QR code. Please try again.');
                console.error('Error:', error);
            }
        });

        // Handle download button
        document.getElementById('downloadBtn').addEventListener('click', () => {
            if (currentQRData) {
                const link = document.createElement('a');
                link.href = 'data:image/png;base64,' + currentQRData;
                link.download = 'qrcode_' + Date.now() + '.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Main page"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(HTML_TEMPLATE, 
                                 current_time=current_time,
                                 qr_count=len(qr_history))

@app.route('/generate', methods=['POST'])
def generate_qr():
    """Generate QR code"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Store in history
        qr_history.append({
            'text': text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return jsonify({
            "success": True,
            "qr_code": img_base64,
            "total_generated": len(qr_history)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "QR Code Generator - DevOps Pipeline",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "qr_codes_generated": len(qr_history),
        "message": "All systems operational"
    })

@app.route('/stats')
def stats():
    """Statistics page"""
    return jsonify({
        "total_qr_codes": len(qr_history),
        "recent_qr_codes": qr_history[-5:] if qr_history else [],
        "status": "Live",
        "deployed_on": "AWS EC2",
        "team": "PipelineX"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
