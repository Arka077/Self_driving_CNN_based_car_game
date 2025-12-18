# CNN Car Game - AI-Controlled Racing Game

An autonomous racing game powered by a Convolutional Neural Network (CNN) that learns to navigate a car through traffic by recognizing road conditions and making real-time driving decisions. The car is controlled entirely by AI predictions based on visual input.

## 🎯 Project Overview

This project combines deep learning and game development to create an intelligent agent that drives a car autonomously. A trained CNN model analyzes the game screen in real-time and predicts driving actions (left, center, or right movements), enabling the car to navigate lanes and avoid obstacles without manual input.

### Key Features

- **CNN-Powered Autonomous Control**: Real-time predictions for driving actions
- **Interactive Game Engine**: Built with Pygame for smooth, real-time rendering
- **Lane-Based Navigation**: Three-lane road system with dynamic traffic
- **Score System**: Tracks performance and high scores
- **Model Training Pipeline**: Complete Jupyter notebook for training custom models
- **Data Collection**: Automatic frame capture for dataset generation
- **Computer Vision**: OpenCV-based image preprocessing (YUV conversion, blur, resize)

## 📁 Project Structure

```
CNN car/
├── main.py                 # Main game loop with AI-controlled car
├── car.py                  # Car physics and control logic
├── road.py                 # Road and traffic management
├── model_predictor.py      # CNN model loading and prediction inference
├── dataset_generator.py    # Data collection utilities
├── train_model.ipynb       # Model training and evaluation notebook
├── best_model.h5           # Pre-trained CNN model weights
├── requirements.txt        # Project dependencies
└── dataset/
    ├── left/               # Training data: left turn samples
    ├── no_action/          # Training data: center/no action samples
    └── right/              # Training data: right turn samples
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CNN-car-game.git
cd CNN\ car
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Quick Start

Run the AI-controlled car game:
```bash
python main.py
```

The car will automatically navigate the road based on the pre-trained CNN model.

## 📦 Dependencies

- **TensorFlow/Keras** (≥2.0): Deep learning framework for CNN model
- **Pygame** (≥2.0.0): Game engine and rendering
- **OpenCV** (≥4.5.0): Computer vision and image preprocessing
- **NumPy** (≥1.19.0): Numerical computations

## 🎮 How It Works

### Game Loop (`main.py`)
1. Captures the current game screen at 60 FPS
2. Feeds the screen to the CNN model for inference
3. Model predicts driving action (SWIPE_LEFT, CENTER, or SWIPE_RIGHT)
4. Updates car position and lane based on prediction
5. Renders updated game state
6. Tracks score based on obstacles avoided and distance traveled

### Model Architecture
- **Input**: Preprocessed game frames (200×400 pixels, YUV color space)
- **Processing**: 
  - Gaussian blur for noise reduction
  - YUV color space conversion (more robust than RGB for driving scenarios)
  - Normalization to [0, 1] range
- **Output**: Probabilities for 3 classes (left, center, right)
- **Action**: Selects class with highest confidence

### Car Control (`car.py`)
- Smooth lane transitions with physics-based movement
- Three-lane system for navigation
- Velocity and acceleration simulation
- Collision detection and braking mechanics

## 📊 Training the Model

To train a custom model:

1. Open `train_model.ipynb` in Jupyter:
```bash
jupyter notebook train_model.ipynb
```

2. The notebook includes:
   - Dataset loading and preprocessing
   - CNN model architecture definition
   - Model training with validation
   - Performance evaluation and visualization

3. Save your trained model as `best_model.h5` to use it in the game

## 🎯 Training Data Format

Training data is organized into three categories under `dataset/`:
- **left/**: Images of road conditions requiring left lane change
- **no_action/**: Images of road conditions requiring center/straight driving
- **right/**: Images of road conditions requiring right lane change

Use `dataset_generator.py` to collect new training data during gameplay.

## 🔧 Configuration

### Key Parameters (`main.py`)

- `SCREEN_WIDTH` / `SCREEN_HEIGHT`: Game window dimensions (600×800)
- `FPS`: Frame rate (60)
- `prediction_interval`: Time between model predictions (0.5 seconds)
- `max_velocity`: Maximum car speed
- `lane_change_speed`: Speed of lane transitions

### Model Path

Default model: `best_model.h5`

To use a different model:
```python
game = ModelControlledCarGame(model_path='path/to/your/model.h5')
```

## 📈 Model Performance

- **Input Size**: 200×400 pixels
- **Classes**: 3 (SWIPE_LEFT, CENTER, SWIPE_RIGHT)
- **Preprocessing**: YUV color space, Gaussian blur, normalization
- **Inference Speed**: Real-time at 60 FPS

## 🛠️ Usage Examples

### Run the Game
```bash
python main.py
```

### Custom Model Path
Edit `main.py`:
```python
game = ModelControlledCarGame(model_path='custom_model.h5', prediction_interval=0.5)
```

### Data Collection
```python
from dataset_generator import DatasetGenerator
generator = DatasetGenerator()
# Use during gameplay to collect training data
```

## 📝 File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | Game loop, AI integration, and rendering |
| `car.py` | Car physics, movement, and lane management |
| `road.py` | Road generation, traffic, and collision detection |
| `model_predictor.py` | CNN model loading, preprocessing, and inference |
| `dataset_generator.py` | Utilities for collecting training data |
| `train_model.ipynb` | Jupyter notebook for model training |
| `best_model.h5` | Pre-trained CNN model weights |

## 🎓 Learning Outcomes

This project demonstrates:
- **Deep Learning**: CNN architecture and inference
- **Computer Vision**: Image preprocessing and feature extraction
- **Game Development**: Real-time rendering and physics simulation
- **AI Integration**: Connecting ML models to game engines
- **Data Collection**: Supervised learning dataset generation

## 🐛 Troubleshooting

### Model Not Loading
- Ensure `best_model.h5` exists in the project root
- Verify TensorFlow/Keras are correctly installed: `pip install tensorflow keras`

### Game Running Slowly
- Close other applications
- Reduce `FPS` if needed
- Increase `prediction_interval` for fewer predictions

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## 🤝 Contributing

Contributions are welcome! You can:
- Improve the CNN model architecture
- Add new game features (traffic, obstacles, etc.)
- Enhance the preprocessing pipeline
- Expand training datasets

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created as a deep learning and game development project combining CNN inference with interactive Pygame simulation.

## 🔗 References

- [TensorFlow/Keras Documentation](https://www.tensorflow.org/)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Convolutional Neural Networks](https://en.wikipedia.org/wiki/Convolutional_neural_network)

---

**Enjoy the AI-controlled car game!** 🚗🤖
