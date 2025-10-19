"""
VAMedRec - Web API Entry Point
Handles HTTP requests and responses for medication reconciliation service.
"""

from flask import Flask, request, jsonify, render_template_string
from typing import Dict
import config
from core.reconciler import MedicationReconciler

# Initialize Flask app
app = Flask(__name__)

# Initialize reconciler
reconciler = MedicationReconciler()


@app.route('/', methods=['GET'])
def home():
    """Home page with API documentation."""
    html = """    <!DOCTYPE html>
    <html>
    <head>
        <title>VAMedRec - VA Medication Reconciliation API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }
            h2 { color: #555; margin-top: 30px; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: "Courier New", monospace;
            }
            pre {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 20px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .endpoint {
                background: #e8f4f8;
                padding: 15px;
                border-left: 4px solid #007acc;
                margin: 20px 0;
            }
            .method { 
                display: inline-block;
                background: #007acc;
                color: white;
                padding: 4px 8px;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
        </style>
    </head>    <body>
        <div class="container">
            <h1>🏥 VAMedRec - VA Medication Reconciliation API</h1>
            <p>
                A hybrid system combining AI-powered clinical reasoning with deterministic safety checks
                for comprehensive VA medication reconciliation.
            </p>

            <h2>🔌 Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <code>/reconcile</code>
                <p>Perform medication reconciliation</p>
            </div>

            <div class="endpoint">
                <span class="method">GET</span>
                <code>/health</code>
                <p>Check API health status</p>
            </div>

            <h2>📝 Example Request</h2>
            <pre>{
  "mode": "simple",
  "baseline_meds": [
    "Aspirin 81mg tablet by mouth daily",
    "Metformin 500mg tablet by mouth twice daily"
  ],
  "reference_meds": [
    "Aspirin 81mg daily",
    "Metformin 1000mg daily"
  ],
  "baseline_label": "Inpatient on Admission",
  "reference_label": "Outpatient Home Meds"
}</pre>

            <h2>🎯 Modes</h2>
            <ul>
                <li><strong>simple</strong>: Quick daily reconciliation</li>
                <li><strong>comprehensive</strong>: Full admission/discharge reconciliation with patient context</li>
            </ul>

            <h2>🔐 Safety Features</h2>
            <ul>
                <li>✅ Normalization & standardization</li>
                <li>✅ Duplicate detection</li>
                <li>✅ Drug interaction checking</li>
                <li>✅ Renal/hepatic contraindication alerts</li>
                <li>✅ Complete audit ledger</li>
                <li>✅ Hallucination prevention</li>
            </ul>

            <h2>📚 Documentation</h2>
            <p>
                For detailed documentation, see <code>README.md</code> and <code>DEVLOG.md</code>
                in the project repository.
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Docker and monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "VAMedRec",
        "version": "1.0.0"
    }), 200


@app.route('/reconcile', methods=['POST'])
def reconcile():
    """
    Main reconciliation endpoint.
    
    Expected JSON body:
    {
        "mode": "simple" | "comprehensive",
        "baseline_meds": [...],
        "reference_meds": [...],
        "baseline_label": "...",
        "reference_label": "...",
        "patient_context": {...}  // optional, for comprehensive mode
    }
    """
    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract required fields
        mode = data.get("mode", "simple")
        baseline_meds = data.get("baseline_meds", [])
        reference_meds = data.get("reference_meds", [])
        baseline_label = data.get("baseline_label", "Current (Now)")
        reference_label = data.get("reference_label", "Previous (Then)")
        patient_context = data.get("patient_context")
        
        # Validate inputs
        if not baseline_meds and not reference_meds:
            return jsonify({
                "error": "At least one medication list (baseline_meds or reference_meds) is required"
            }), 400
        
        if mode not in ["simple", "comprehensive"]:
            return jsonify({
                "error": "Invalid mode. Must be 'simple' or 'comprehensive'"
            }), 400
        
        # Perform reconciliation
        result = reconciler.reconcile(
            baseline_meds=baseline_meds,
            reference_meds=reference_meds,
            mode=mode,
            patient_context=patient_context,
            baseline_label=baseline_label,
            reference_label=reference_label
        )
        
        # Format output
        formatted_output = reconciler.format_output(result)
        
        # Return response
        return jsonify({
            "success": True,
            "mode": mode,
            "reconciliation": {
                "markdown": formatted_output,
                "llm_output": result["llm_output"],
                "safety_issues": [
                    {
                        "severity": issue.severity,
                        "category": issue.category,
                        "description": issue.description,
                        "affected_meds": issue.affected_meds
                    }
                    for issue in result["safety_issues"]
                ],
                "ledger_validation": result["ledger_validation"],
                "ledger_summary": result["ledger"].get_summary()
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/reconcile"]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500


if __name__ == '__main__':
    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)
    
    # Run Flask app
    print(f"\n🚀 Starting Medication Reconciliation API")
    print(f"📍 Server: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"📖 Documentation: http://localhost:{config.FLASK_PORT}/")
    print(f"\nPress CTRL+C to stop\n")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
