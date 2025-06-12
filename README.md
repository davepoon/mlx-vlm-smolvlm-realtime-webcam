# 🤖 MLX-VLM SmolVLM Real-time Webcam

A real-time webcam application powered by **SmolVLM** (Small Vision Language Model) running on Apple Silicon using **MLX-VLM**. This application provides a beautiful web interface where you can analyze webcam footage in real-time using AI vision language models.

## ✨ Features

- 🎥 **Real-time Webcam Analysis** - Capture and analyze webcam frames instantly
- 🧠 **SmolVLM Integration** - Powered by efficient SmolVLM models via MLX-VLM
- 🌐 **Web Interface** - Beautiful, responsive web UI with modern design
- ⚡ **Real-time Processing** - Fast inference on Apple Silicon devices
- 🎛️ **Customizable Settings** - Adjust prompts, temperature, tokens, and auto-analysis
- 📱 **Mobile Friendly** - Responsive design works on various screen sizes
- 🔄 **Auto Analysis** - Optional automatic frame analysis at set intervals

## 🚀 Quick Start

### Prerequisites

- **Apple Silicon Mac** (M1, M2, M3, or newer)
- **Python 3.10+**
- **Webcam or camera access**

### Installation

1. **Clone or download the application**
   ```bash
   # If you have the file locally, navigate to the directory
   cd /path/to/your/mlx-projects
   ```

2. **Install dependencies**
   ```bash
   # Install MLX-VLM (the key dependency)
   pip install mlx-vlm
   
   # Install web server dependencies
   pip install flask flask-socketio
   
   # Install image processing
   pip install pillow
   ```

3. **Run the application**
   ```bash
   python mlx_smolvlm_webcam.py --model mlx-community/SmolVLM-Instruct-4bit --port 8080
   ```

4. **Open your browser**
   - Navigate to: `http://localhost:8080`
   - Click "Start Camera" to enable webcam
   - Click "📸 Analyze Frame" to get AI descriptions

## 📋 Requirements

### Essential Dependencies
```bash
pip install mlx-vlm flask flask-socketio pillow
```

### Supported Models
- `mlx-community/SmolVLM-Instruct-4bit` (default, recommended)
- `mlx-community/SmolVLM-Instruct` 
- Other SmolVLM models from mlx-community

## 🎯 Usage

### Basic Usage
```bash
python mlx_smolvlm_webcam.py --model mlx-community/SmolVLM-Instruct-4bit
```

### Advanced Options
```bash
python mlx_smolvlm_webcam.py \
  --model mlx-community/SmolVLM-Instruct-4bit \
  --host 127.0.0.1 \
  --port 8080 \
  --debug
```

### Command Line Arguments
- `--model`: HuggingFace model ID (default: `mlx-community/SmolVLM-Instruct-4bit`)
- `--host`: Server host (default: `127.0.0.1`)
- `--port`: Server port (default: `5000`)
- `--debug`: Enable debug mode

## 🎛️ Web Interface Features

### Camera Controls
- **Start Camera**: Enable webcam access
- **📸 Analyze Frame**: Capture and analyze current frame
- **⏸️ Pause/▶️ Resume**: Toggle camera feed

### Settings Panel
- **Custom Prompt**: Customize what you want the AI to describe
- **Max Tokens**: Control response length (10-500)
- **Temperature**: Adjust creativity/randomness (0.1-2.0)
- **Auto Analyze**: Automatic analysis every 3/5/10 seconds

### Example Prompts
- "Describe what you see in this image in detail"
- "What objects are visible in this scene?"
- "Analyze the emotions and expressions of people in this image"
- "Describe the lighting and composition of this scene"
- "What activities are taking place in this image?"

## 🔧 Troubleshooting

### Common Issues

**"Module not found: flask_socketio"**
```bash
pip install flask-socketio
```

**"Model type idefics3 not supported"**
- Make sure you're using `mlx-vlm` not `mlx-lm`
```bash
pip uninstall mlx-lm
pip install mlx-vlm
```

**"Port already in use"**
```bash
# Use a different port
python mlx_smolvlm_webcam.py --port 8080
```

**Camera permission denied**
- Allow camera access in your browser
- Check System Preferences > Security & Privacy > Camera

**Model loading fails**
```bash
# Clear HuggingFace cache and retry
rm -rf ~/.cache/huggingface/
python mlx_smolvlm_webcam.py --model mlx-community/SmolVLM-Instruct-4bit
```

### Performance Tips

1. **Use 4-bit models** for faster inference:
   ```bash
   --model mlx-community/SmolVLM-Instruct-4bit
   ```

2. **Adjust image size** - App automatically resizes to 512px max dimension

3. **Lower max tokens** for faster responses

4. **Use auto-analyze sparingly** to avoid overwhelming the model

## 🏗️ Architecture

- **Backend**: Flask + SocketIO for real-time communication
- **Frontend**: Modern HTML5 + JavaScript with WebSocket
- **AI Model**: SmolVLM via MLX-VLM for Apple Silicon optimization
- **Image Processing**: PIL for image handling and resizing

## 🎨 Features in Detail

### Real-time Analysis
The application captures webcam frames and sends them to SmolVLM for analysis. The AI provides detailed descriptions of what it sees, including objects, people, activities, and scenes.

### Modern Web Interface
- Gradient backgrounds and modern CSS
- Responsive design for different screen sizes
- Real-time status indicators
- Smooth animations and transitions

### Flexible Configuration
- Adjustable AI parameters (temperature, max tokens)
- Custom prompts for specific use cases
- Auto-analysis for continuous monitoring

## 📝 Example Outputs

**Scene Description**:
> "I can see a person sitting at a desk with a laptop computer. There are books and papers scattered on the desk, and a window with natural lighting in the background. The person appears to be working or studying."

**Object Detection**:
> "In this image, I can identify: a laptop computer, several books, a coffee mug, a desk lamp, and a potted plant on the windowsill."

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

## 📄 License

This project is open source. Please check individual dependencies for their respective licenses.

## 🙏 Acknowledgments

- **SmolVLM**: HuggingFace's efficient vision language model
- **MLX**: Apple's machine learning framework for Apple Silicon
- **MLX-VLM**: MLX integration for vision language models

---

**Enjoy analyzing the world through AI! 🎉**