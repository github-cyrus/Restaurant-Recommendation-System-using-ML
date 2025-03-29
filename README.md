# Restaurant Recommendation System

A modern web application that helps users find restaurants based on their preferences, including cost, rating, and various amenities.

## Features

- Interactive and responsive UI
- Advanced filtering options
- Real-time map visualization
- Personalized recommendations using machine learning
- Beautiful restaurant cards with images
- Mobile-friendly design

## Prerequisites

- Python 3.8 or higher
- Node.js (for running a local server if needed)
- Modern web browser

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd restaurant-recommendation-system
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask backend server:
```bash
cd api
python app.py
```
The server will start at `http://localhost:5000`

2. Open `index.html` in your web browser
   - You can use a simple HTTP server to serve the frontend:
   ```bash
   python -m http.server 8000
   ```
   Then visit `http://localhost:8000` in your browser

## Project Structure

```
restaurant-recommendation-system/
├── api/
│   └── app.py           # Flask backend server
├── dataset/
│   └── restaurant.csv   # Restaurant dataset
├── images/              # Image assets
├── index.html          # Main frontend page
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## API Endpoints

- `POST /api/recommend`: Get restaurant recommendations
  - Request body: JSON with user preferences
  - Response: List of recommended restaurants

- `GET /api/health`: Health check endpoint
  - Response: Server status and timestamp

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 