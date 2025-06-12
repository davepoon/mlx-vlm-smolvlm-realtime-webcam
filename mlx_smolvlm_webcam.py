#!/usr/bin/env python3

import argparse
import base64
import io
from typing import Optional

from flask import Flask, render_template_string
from flask_socketio import SocketIO
from PIL import Image

try:
    from mlx_vlm import load, generate
    from mlx_vlm.utils import load_config
except ImportError:
    print("Error: mlx-vlm is required. Install with: pip install mlx-vlm")
    exit(1)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLX SmolVLM Real-time Webcam</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
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
            color: white;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 20px;
        }

        .video-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .response-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        #video {
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .controls {
            margin-top: 15px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }

        button:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4ecdc4;
            animation: pulse 2s infinite;
        }

        .status-indicator.processing {
            background: #ff9f43;
        }

        .status-indicator.error {
            background: #ff6b6b;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }

        #response {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 20px;
            min-height: 200px;
            font-size: 16px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .prompt-input {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .prompt-input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }

        .settings {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .settings h3 {
            margin-bottom: 15px;
        }

        .setting-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .setting-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .setting-item label {
            font-size: 14px;
            font-weight: 500;
        }

        .setting-item input, .setting-item select {
            padding: 8px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 14px;
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 2em;
            }
        }

        .error-message {
            background: rgba(255, 107, 107, 0.2);
            border: 1px solid #ff6b6b;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .analyzing-message {
            color: #666;
            padding: 5px 0;
            border-top: 1px solid #eee;
            margin-top: 10px;
            animation: pulse 1.5s ease-in-out infinite;
            color: #fff;
        }
        
        .previous-response {
            opacity: 0.7;
            margin-bottom: 5px;
        }
        
        @keyframes pulse {
            0% { opacity: 0.5; }
            50% { opacity: 1; }
            100% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 MLX SmolVLM Real-time Webcam</h1>
        
        <div class="main-content">
            <div class="video-section">
                <div class="status">
                    <div class="status-indicator" id="statusIndicator"></div>
                    <span id="statusText">Initializing...</span>
                </div>
                
                <video id="video" autoplay muted playsinline></video>
                
                <div class="controls">
                    <button id="startCamera">Start Camera</button>
                    <button id="analyzeBtn" disabled>📸 Analyze Frame</button>
                    <button id="toggleCamera" disabled>⏸️ Pause</button>
                </div>
            </div>
            
            <div class="response-section">
                <h3>🧠 AI Response</h3>
                <div id="errorContainer"></div>
                <div id="response">Click "Start Camera" and then "Analyze Frame" to begin...</div>
            </div>
        </div>
        
        <div class="settings">
            <h3>⚙️ Settings</h3>
            <div class="setting-group">
                <div class="setting-item">
                    <label for="promptInput">Custom Prompt:</label>
                    <input type="text" id="promptInput" class="prompt-input" 
                           placeholder="Briefly describe what you see...">
                </div>
                <div class="setting-item">
                    <label for="maxTokens">Max Tokens:</label>
                    <input type="number" id="maxTokens" value="30" min="5" max="50">
                </div>
                <div class="setting-item">
                    <label for="temperature">Temperature:</label>
                    <input type="number" id="temperature" value="0.2" min="0.1" max="1.0" step="0.1">
                </div>
                <div class="setting-item">
                    <label for="autoAnalyze">Auto Analyze:</label>
                    <select id="autoAnalyze">
                        <option value="false">Manual</option>
                        <option value="0.5">Every 0.5 seconds (Ultra Fast)</option>
                        <option value="1">Every 1 second (Fast)</option>
                        <option value="1.5">Every 1.5 seconds</option>
                        <option value="2" selected>Every 2 seconds (Balanced)</option>
                        <option value="3">Every 3 seconds</option>
                        <option value="5">Every 5 seconds (Slow)</option>
                        <option value="10">Every 10 seconds (Very Slow)</option>
                    </select>
                </div>
            </div>
        </div>
    </div>

    <script>
        class SmolVLMWebcam {
            constructor() {
                this.socket = io();
                this.video = document.getElementById('video');
                this.canvas = document.createElement('canvas');
                this.ctx = this.canvas.getContext('2d');
                this.stream = null;
                this.isProcessing = false;
                this.autoAnalyzeInterval = null;
                
                this.initializeElements();
                this.setupSocketEvents();
                this.setupEventListeners();
            }
            
            initializeElements() {
                this.startCameraBtn = document.getElementById('startCamera');
                this.analyzeBtn = document.getElementById('analyzeBtn');
                this.toggleCameraBtn = document.getElementById('toggleCamera');
                this.statusIndicator = document.getElementById('statusIndicator');
                this.statusText = document.getElementById('statusText');
                this.responseDiv = document.getElementById('response');
                this.errorContainer = document.getElementById('errorContainer');
                this.promptInput = document.getElementById('promptInput');
                this.maxTokensInput = document.getElementById('maxTokens');
                this.temperatureInput = document.getElementById('temperature');
                this.autoAnalyzeSelect = document.getElementById('autoAnalyze');
            }
            
            setupSocketEvents() {
                this.socket.on('connect', () => {
                    console.log('Connected to server');
                    this.updateStatus('connected', 'Connected to server');
                });
                
                this.socket.on('disconnect', () => {
                    console.log('Disconnected from server');
                    this.updateStatus('error', 'Disconnected from server');
                });
                
                this.socket.on('analysis_result', (data) => {
                    this.handleAnalysisResult(data);
                });
                
                this.socket.on('error', (data) => {
                    this.handleError(data.message);
                });
            }
            
            setupEventListeners() {
                this.startCameraBtn.addEventListener('click', () => this.startCamera());
                this.analyzeBtn.addEventListener('click', () => this.analyzeFrame());
                this.toggleCameraBtn.addEventListener('click', () => this.toggleCamera());
                this.autoAnalyzeSelect.addEventListener('change', () => this.updateAutoAnalyze());
            }
            
            async startCamera() {
                try {
                    this.stream = await navigator.mediaDevices.getUserMedia({ 
                        video: { width: 640, height: 480 } 
                    });
                    this.video.srcObject = this.stream;
                    
                    this.startCameraBtn.disabled = true;
                    this.analyzeBtn.disabled = false;
                    this.toggleCameraBtn.disabled = false;
                    
                    this.updateStatus('ready', 'Camera ready');
                    this.clearError();
                    
                    // Wait for video to be ready, then start auto-analyze if selected
                    this.video.addEventListener('loadeddata', () => {
                        this.updateAutoAnalyze(); // Restart auto-analyze now that camera is ready
                    });
                    
                } catch (error) {
                    this.handleError('Failed to access camera: ' + error.message);
                }
            }
            
            captureFrame() {
                if (!this.stream) return null;
                
                this.canvas.width = this.video.videoWidth;
                this.canvas.height = this.video.videoHeight;
                this.ctx.drawImage(this.video, 0, 0);
                
                return this.canvas.toDataURL('image/jpeg', 0.8);
            }
            
            analyzeFrame() {
                if (this.isProcessing) return;
                
                const frameData = this.captureFrame();
                if (!frameData) {
                    this.handleError('No camera frame available');
                    return;
                }
                
                this.isProcessing = true;
                this.updateStatus('processing', 'Processing...');
                this.analyzeBtn.disabled = true;
                
                // Show analyzing message while keeping previous response visible
                const currentResponse = this.responseDiv.textContent;
                if (currentResponse) {
                    this.responseDiv.innerHTML = `<div class="previous-response">${currentResponse}</div><div class="analyzing-message">🔍 Analyzing...</div>`;
                } else {
                    this.responseDiv.innerHTML = '<div class="analyzing-message">🔍 Analyzing...</div>';
                }
                
                const prompt = this.promptInput.value.trim() || 'Tell me what you see.';
                const maxTokens = parseInt(this.maxTokensInput.value) || 30;
                const temperature = parseFloat(this.temperatureInput.value) || 0.2;
                
                this.socket.emit('analyze_frame', {
                    image: frameData,
                    prompt: prompt,
                    max_tokens: maxTokens,
                    temperature: temperature
                });
            }
            
            handleAnalysisResult(data) {
                this.isProcessing = false;
                this.analyzeBtn.disabled = false;
                this.updateStatus('ready', 'Analysis complete');
                
                if (data.success) {
                    this.responseDiv.textContent = data.response;
                    this.clearError();
                } else {
                    this.handleError(data.error || 'Analysis failed');
                }
            }
            
            toggleCamera() {
                if (this.video.srcObject) {
                    const tracks = this.video.srcObject.getTracks();
                    tracks.forEach(track => {
                        track.enabled = !track.enabled;
                    });
                    
                    const isEnabled = tracks[0].enabled;
                    this.toggleCameraBtn.textContent = isEnabled ? '⏸️ Pause' : '▶️ Resume';
                    this.updateStatus(isEnabled ? 'ready' : 'paused', 
                                    isEnabled ? 'Camera ready' : 'Camera paused');
                }
            }
            
            updateAutoAnalyze() {
                if (this.autoAnalyzeInterval) {
                    clearInterval(this.autoAnalyzeInterval);
                    this.autoAnalyzeInterval = null;
                }
                
                const interval = this.autoAnalyzeSelect.value;
                if (interval !== 'false') {
                    const intervalMs = parseFloat(interval) * 1000;
                    this.autoAnalyzeInterval = setInterval(() => {
                        // Check if camera is ready and not currently processing
                        if (!this.isProcessing && this.stream && this.video.readyState >= 2) {
                            this.analyzeFrame();
                        }
                    }, intervalMs);
                    
                    console.log(`Auto-analyze started: every ${interval} second(s) (${intervalMs}ms)`);
                }
            }
            
            updateStatus(type, message) {
                this.statusIndicator.className = `status-indicator ${type}`;
                this.statusText.textContent = message;
            }
            
            handleError(message) {
                console.error('Error:', message);
                this.errorContainer.innerHTML = `<div class="error-message">❌ Error: ${message}</div>`;
                this.updateStatus('error', 'Error occurred');
                this.isProcessing = false;
                this.analyzeBtn.disabled = false;
            }
            
            clearError() {
                this.errorContainer.innerHTML = '';
            }
        }
        
        // Initialize the application
        document.addEventListener('DOMContentLoaded', () => {
            new SmolVLMWebcam();
        });
    </script>
</body>
</html>
"""

class MLXSmolVLMWebServer:
    def __init__(self, model_path: str, host: str = "localhost", port: int = 8080):
        """Initialize the MLX SmolVLM web server."""
        self.model_path = model_path
        self.host = host
        self.port = port
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'smolvlm-secret-key'
        
        # Add CORS and security headers
        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
            return response
        
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", logger=True, engineio_logger=True)
        
        # Model will be loaded on first use
        self.model = None
        self.processor = None
        self.config = None
        self.model_loading = False
        
        self.setup_routes()
        self.setup_socket_events()
    
    def load_model(self):
        """Load the model with optimized configuration."""
        if self.model is None and not self.model_loading:
            self.model_loading = True
            try:
                print(f"Loading optimized model: {self.model_path}")
                
                # Load model with MLX optimizations
                self.model, self.processor = load(self.model_path)
                self.config = load_config(self.model_path)
                
                # Optimize processor for faster inference
                # Set image resolution for speed (N=2 for 768x768, faster than default 1536x1536)
                if hasattr(self.processor, 'image_processor'):
                    self.processor.image_processor.size = {"longest_edge": 2 * 384}  # 768px max
                
                print("✅ Model loaded with optimizations!")
                print(f"📊 Image processing size: {self.processor.image_processor.size if hasattr(self.processor, 'image_processor') else 'default'}")
                return True
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                self.model_loading = False
                return False
            finally:
                self.model_loading = False
        return self.model is not None
    
    def ensure_complete_sentences(self, text: str) -> str:
        """Ensure the response ends with complete sentences only."""
        if not text:
            return text
        
        # Common sentence endings
        sentence_endings = ['.', '!', '?']
        
        # If text already ends with proper punctuation, return as is
        if text[-1] in sentence_endings:
            return text
        
        # Find the last complete sentence
        last_complete = -1
        for i, char in enumerate(text):
            if char in sentence_endings:
                # Check if this is really the end of a sentence (not an abbreviation)
                if i + 1 < len(text) and text[i + 1] in [' ', '\n', '\t']:
                    last_complete = i
                elif i == len(text) - 1:  # End of text
                    last_complete = i
        
        # If we found a complete sentence, truncate there
        if last_complete > 0:
            return text[:last_complete + 1].strip()
        
        # If no complete sentence found, try to end at a logical break point
        logical_breaks = [',', ';', ':']
        for break_char in logical_breaks:
            last_break = text.rfind(break_char)
            if last_break > len(text) * 0.7:  # Only if it's near the end
                return text[:last_break].strip() + '.'
        
        # As last resort, find the last complete word and add a period
        words = text.split()
        if len(words) > 1:
            # Remove the last word if it seems incomplete
            last_word = words[-1]
            if not last_word.endswith(('.', '!', '?', ',', ';', ':')):
                words = words[:-1]
            return ' '.join(words) + '.'
        
        return text
    
    def setup_routes(self):
        """Setup Flask routes."""
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
    
    def setup_socket_events(self):
        """Setup Socket.IO events."""
        @self.socketio.on('connect')
        def handle_connect():
            print("Client connected")
            # Load model in background if not loaded
            if not self.load_model():
                self.socketio.emit('error', {'message': 'Failed to load model'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected")
        
        @self.socketio.on('analyze_frame')
        def handle_analyze_frame(data):
            """Handle frame analysis request."""
            if not self.model or not self.processor or not self.config:
                if not self.load_model():
                    self.socketio.emit('analysis_result', {
                        'success': False,
                        'error': 'Model not loaded'
                    })
                    return
            
            try:
                # Decode base64 image
                image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64,
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Get parameters - optimized for speed
                prompt = data.get('prompt', 'What do you see?')
                max_tokens = data.get('max_tokens', 30)  # Reduced for faster generation
                temperature = data.get('temperature', 0.2)  # Lower for faster, more focused responses
                
                # Optimize image size according to SmolVLM recommendations
                # SmolVLM uses 384x384 patches, so we optimize for that
                max_size = 768  # N=2 * 384 for good speed/quality balance
                if max(image.size) > max_size:
                    # Use LANCZOS for better quality at this resolution
                    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                print(f"📸 Image processed: {image.size} (original) -> {image.size} (processed)")
                
                # Use the MLX-VLM generate function directly
                # Format prompt with image placeholder
                formatted_prompt = f"<image>\n{prompt}"
                
                # Generate response with speed optimizations
                import time
                start_time = time.time()
                
                response = generate(
                    model=self.model,
                    processor=self.processor,
                    prompt=formatted_prompt,
                    image=image,
                    verbose=False,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    repetition_penalty=1.0,  # Reduce repetition processing
                    repetition_context_size=0  # Disable repetition context for speed
                )
                
                inference_time = time.time() - start_time
                print(f"Inference time: {inference_time:.2f}s")
                
                # Handle response - check if it's a tuple first
                if isinstance(response, tuple):
                    # If it's a tuple, take the first element (usually the text)
                    response = response[0]
                elif isinstance(response, list):
                    response = " ".join(str(r) for r in response)
                
                # Ensure response is a string before calling replace
                if not isinstance(response, str):
                    response = str(response)
                
                # Clean up response
                response = response.replace("<|im_start|>", "").replace("<|im_end|>", "").strip()
                
                # Ensure complete sentences
                response = self.ensure_complete_sentences(response)
                
                if not response:
                    response = "No response generated."
                
                self.socketio.emit('analysis_result', {
                    'success': True,
                    'response': response
                })
                
                print(f"Analysis complete: {response[:100]}...")
                
            except Exception as e:
                error_msg = f"Analysis error: {str(e)}"
                print(error_msg)
                self.socketio.emit('analysis_result', {
                    'success': False,
                    'error': error_msg
                })
    
    def run(self):
        """Run the web server."""
        print(f"Starting MLX SmolVLM Web Server...")
        print(f"Open your browser and go to: http://{self.host}:{self.port}")
        print("Press Ctrl+C to stop the server")
        
        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=True,
                allow_unsafe_werkzeug=True,
                use_reloader=False,
                log_output=True
            )
        except KeyboardInterrupt:
            print("\nShutting down server...")

def main():
    parser = argparse.ArgumentParser(description="MLX SmolVLM Real-time Webcam Web Server")
    parser.add_argument("--model", type=str, default="mlx-community/SmolVLM-Instruct-4bit",
                       help="Path or HuggingFace model ID for SmolVLM model. Recommended: HuggingFaceTB/SmolVLM-Instruct")
    parser.add_argument("--host", type=str, default="127.0.0.1",
                       help="Host to bind the server (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080,
                       help="Port to bind the server (default: 8080)")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Try different hosts if localhost fails
    if args.host == "localhost":
        args.host = "127.0.0.1"
    
    print(f"🚀 Starting MLX SmolVLM Web Server...")
    print(f"📱 Model: {args.model}")
    print(f"🌐 Server: http://{args.host}:{args.port}")
    print(f"🔧 Debug: {args.debug}")
    print("=" * 50)
    
    try:
        server = MLXSmolVLMWebServer(
            model_path=args.model,
            host=args.host,
            port=args.port
        )
        server.run()
    except PermissionError:
        print(f"❌ Permission denied on port {args.port}")
        print("💡 Try a different port: --port 8080")
        return 1
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {args.port} is already in use")
            print("💡 Try a different port: --port 8080")
        else:
            print(f"❌ Network error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())