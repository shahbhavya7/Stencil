# 🎨 Stencil

**Professional AI-Powered Image Generation & Editing Platform**

Stencil is a comprehensive Streamlit-based web application that leverages Bria AI's powerful APIs to provide professional image generation, editing, and enhancement capabilities.

## ✨ Features

### 🎨 AI Image Generation

- **Text-to-Image Generation**: Create stunning images from textual descriptions
- **Prompt Enhancement**: AI-powered prompt optimization for better results
- **Multiple Style Options**: Realistic, Artistic, Cartoon, Sketch, Watercolor, Oil Painting, Digital Art, 3D Render
- **Customizable Settings**: Aspect ratios, image quality, refinement steps, and more
- **Batch Generation**: Generate multiple variations at once

### 🖼️ Product Photography

- **Lifestyle Shots**: Place products in realistic environments
  - Text-based scene description
  - Reference image-based generation
  - Multiple placement options (automatic, manual, custom coordinates)
- **Packshot Creation**: Professional product photography with clean backgrounds
- **Shadow Addition**: Add realistic shadows to products
  - Natural and drop shadow types
  - Customizable shadow properties

### ✨ Advanced Editing

- **Generative Fill**: Fill selected areas with AI-generated content
  - Interactive mask drawing
  - Prompt-based generation
  - Multiple variations
- **Element Erasing**: Remove unwanted elements from images
  - Brush-based selection
  - Intelligent content-aware fill

### 🎭 Image Filters & Enhancement

- **Creative Filters**: Grayscale, Sepia, Vintage, and more
- **Fine-tune Controls**: Brightness, Contrast, Saturation, Sharpness
- **Professional Effects**: Blur, Sharpen, Edge Enhance
- **Real-time Preview**: See changes instantly

### 📊 Session Management

- **Generation History**: Track all generated images
- **Statistics Dashboard**: Monitor your usage
- **Quick Actions**: Load previous generations, clear history, reset session

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Bria AI API key ([Get one here](https://bria.ai))

### Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd Stencil
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:

   ```env
   BRIA_API_KEY=your_api_key_here
   ```

4. **Run the application**

   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 🎯 Usage

### Generate Images

1. Navigate to the **Generate Image** tab
2. Enter a detailed description of what you want to create
3. (Optional) Click **Enhance Prompt** to optimize your description
4. Adjust generation settings (aspect ratio, style, quality)
5. Click **Generate Images**
6. Download your results

### Create Lifestyle Shots

1. Go to the **Lifestyle Shot** tab
2. Upload your product image
3. Choose between text prompt or reference image
4. Describe the desired environment or upload a reference
5. Configure placement and quality settings
6. Generate your lifestyle shot

### Apply Generative Fill

1. Navigate to **Generative Fill**
2. Upload an image
3. Draw a mask over the area you want to modify
4. Describe what should appear in that area
5. Generate and download the result

### Erase Elements

1. Go to **Erase Elements** tab
2. Upload your image
3. Draw over the elements you want to remove
4. Click **Erase Selected Area**
5. Download the cleaned image

### Apply Filters

1. Navigate to **Image Filters** tab
2. Upload your image
3. Select a filter preset
4. Fine-tune with adjustment sliders
5. Apply and download

## 🏗️ Project Structure

```
Stencil/
├── app.py                      # Main application file
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── README.md                   # This file
│
├── services/                   # API service modules
│   ├── __init__.py
│   ├── hd_image_generation.py
│   ├── prompt_enhancement.py
│   ├── lifestyle_shot.py
│   ├── packshot.py
│   ├── shadow.py
│   ├── generative_fill.py
│   └── erase_foreground.py
│
├── components/                 # UI components (optional)
│   ├── image_preview.py
│   ├── sidebar.py
│   └── uploader.py
│
├── utils/                      # Utility functions
└── workflows/                  # Workflow configurations
```

## 🎨 UI Features

- **Modern Dark Theme**: Sleek gradient-based design
- **Responsive Layout**: Works on different screen sizes
- **Interactive Elements**: Smooth animations and transitions
- **Real-time Feedback**: Loading indicators and status messages
- **Error Handling**: Clear error messages and debugging info
- **Download Support**: Easy one-click downloads

## 🔧 Configuration

### API Settings

Configure API behavior in the sidebar:

- API Key input
- Session statistics
- Generation history
- Quick actions

### Advanced Settings

Each feature includes advanced settings:

- Seed for reproducibility
- Refinement steps
- Guidance scale
- Content moderation
- Quality enhancement

## 📝 Tips for Best Results

### Image Generation

- Be specific and descriptive in your prompts
- Use the prompt enhancement feature for better results
- Experiment with different styles
- Use seeds to reproduce favorite results

### Lifestyle Shots

- Use high-quality product images with clean backgrounds
- Provide detailed scene descriptions
- Try reference images for specific environments
- Adjust placement for optimal composition

### Generative Fill

- Draw clear, precise masks
- Be specific about what should appear in the filled area
- Use negative prompts to avoid unwanted elements
- Generate multiple variations for options

## 🐛 Troubleshooting

### Common Issues

**API Key Not Working**

- Verify your API key is correct
- Check if you have API credits
- Ensure you're connected to the internet

**Images Not Loading**

- Wait a moment and refresh
- Check your internet connection
- Verify the API response in debug info

**Canvas Not Responding**

- Refresh the page
- Clear browser cache
- Try a different browser

**Filters Not Applying**

- Ensure image is uploaded completely
- Check image format (PNG, JPG, JPEG)
- Try with a smaller image

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Bria AI](https://bria.ai) for the powerful API
- [Streamlit](https://streamlit.io) for the amazing framework
- Community contributors and testers

## 📧 Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Contact: your-email@example.com

---

Made with ❤️ by [Your Name]
