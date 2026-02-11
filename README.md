# 💰 Money Mindset

A comprehensive financial education platform that gamifies personal finance learning through interactive simulations, AI-powered tutoring, and personalized financial personality assessments.

## 🌟 Features

### 🎮 Gamification System
- **Achievement Engine**: Earn badges and unlock achievements as you progress
- **Progress Tracking**: Track your financial literacy journey
- **Interactive Challenges**: Complete quests and challenges to learn financial concepts

### 🤖 AI-Powered Learning
- **AI Financial Tutor**: Get personalized financial advice and explanations
- **Smart Recommendations**: Receive tailored suggestions based on your financial personality
- **Context-Aware Help**: Ask questions and get instant answers about financial concepts

### 📊 Advanced Analytics
- **Budget Optimization**: AI-powered budget recommendations
- **Expense Classification**: Automatic categorization of transactions
- **Financial Forecasting**: Predict future financial trends
- **Market Simulation**: Practice investing in simulated markets

### 🎯 Interactive Simulations
- **Coffee Shop Simulator**: Learn about daily spending habits
- **Budget Builder**: Create and manage realistic budgets
- **Investment Simulator**: Practice investment strategies risk-free
- **Debt Analysis**: Understand and plan debt repayment
- **Emergency Fund Calculator**: Plan for unexpected expenses
- **Tax Optimizer**: Learn tax planning strategies
- **Monte Carlo Simulation**: Understand financial probabilities
- **Paycheck Game**: Simulate payday decisions

### 🧠 Personality Assessment
- **Financial Personality Quiz**: Discover your spending and saving style
- **Personalized Insights**: Get recommendations based on your personality type
- **Behavioral Analysis**: Understand your financial decision-making patterns

### 💼 Financial Management
- **Transaction Tracking**: Monitor all your financial activities
- **Goal Setting**: Set and track financial goals
- **Budget Management**: Create and manage multiple budgets
- **Progress Reports**: Visualize your financial progress

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type hints
- **JWT Authentication**: Secure user authentication
- **NumPy & Pandas**: Data analysis and computations

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **GSAP**: Professional-grade animations
- **Recharts**: Data visualization

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **npm or yarn**
- **Git**

## 🚀 Quick Start

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/Atharva-cyber849/Money_Mindset.git
cd Money_Mindset
```

2. **Create and activate virtual environment**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize the database**
```bash
python seed_demo.py
```

6. **Run the backend server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
# or
yarn install
```

3. **Set up environment variables**
```bash
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

4. **Run the development server**
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

## 📁 Project Structure

```
Money_Mindset/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Configuration and security
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   │       ├── ai_tutor/
│   │       ├── analytics/
│   │       ├── gamification/
│   │       ├── personality/
│   │       └── simulation/
│   ├── requirements.txt
│   └── seed_demo.py
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # React components
│   │   └── lib/             # Utilities and helpers
│   ├── package.json
│   └── tailwind.config.js
├── tests/                   # Test files
├── .gitignore
└── README.md
```

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)**: Complete API reference
- **[Quick Start Guide](QUICK_START.md)**: Get started quickly
- **[Demo Account](DEMO_ACCOUNT.md)**: Test with demo data
- **[Project Roadmap](PROJECT_ROADMAP.md)**: Future features and plans
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)**: Technical details
- **[UI Design](frontend/UI_DESIGN_IMPLEMENTATION.md)**: Design system documentation

## 🎯 Usage

### Demo Account
```
Email: demo@moneymindset.com
Password: demo123
```

### Running Demo Scripts

**Coffee Shop Simulator Demo**
```bash
python demo_coffee_shop.py
```

**Analytics Features Demo**
```bash
python demo_analytics_features.py
```

## 🧪 Testing

Run the test suite:
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🔗 API Endpoints

- **Authentication**: `/api/v1/auth`
- **Users**: `/api/v1/users`
- **Transactions**: `/api/v1/transactions`
- **Budgets**: `/api/v1/budgets`
- **Goals**: `/api/v1/goals`
- **AI Tutor**: `/api/v1/ai-tutor`
- **Analytics**: `/api/v1/analytics`
- **Simulations**: `/api/v1/simulations`
- **Personality**: `/api/v1/personality`
- **Progress**: `/api/v1/progress`

Full API documentation available at `http://localhost:8000/docs`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Atharva** - [Atharva-cyber849](https://github.com/Atharva-cyber849)

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape Money Mindset
- Financial education resources and methodologies
- Open source community for amazing tools and libraries

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🌐 Links

- **Repository**: [https://github.com/Atharva-cyber849/Money_Mindset](https://github.com/Atharva-cyber849/Money_Mindset)
- **Issues**: [https://github.com/Atharva-cyber849/Money_Mindset/issues](https://github.com/Atharva-cyber849/Money_Mindset/issues)

---

Made with ❤️ for better financial literacy
