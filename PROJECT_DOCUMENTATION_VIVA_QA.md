# TradeIQ Viva Questions and Answers

## Q1. What is TradeIQ?
TradeIQ is a full-stack web application for stock analysis and prediction support. It provides authenticated access to prediction APIs, historical stock trends, and admin operations.

## Q2. Which development methodology did you follow?
We followed an Agile, sprint-based iterative approach. Features were developed in increments, integrated continuously, and validated with frequent testing.

## Q3. Why Agile for this project?
Agile helped us handle evolving requirements, quickly fix API/runtime issues, and deliver usable modules in each phase.

## Q4. What are the key modules of your system?
Authentication and user roles, prediction API, stock history API, frontend dashboard, admin management, and activity/reporting modules.

## Q5. What technology stack did you use?
Backend: Django, Django REST Framework, JWT authentication
Frontend: React with Vite
ML: Scikit-learn/TensorFlow modules in repository
Data Source: yfinance and dataset CSV

## Q6. How does prediction work in your system?
The API accepts stock input parameters (open, high, low, volume), loads model artifacts, computes predicted value, and returns recommendation (BUY/SELL/HOLD logic).

## Q7. What challenges did you face?
API disconnection, dependency mismatch, environment-specific configuration issues, and model-loading reliability.

## Q8. How were the challenges solved?
By health-check-based debugging, dependency correction, environment-variable configuration, and verification through end-to-end API tests.

## Q9. What are your proposed enhancements?
PostgreSQL migration, model versioning, async processing, real-time updates, stronger security policies, and CI/CD-based automated quality checks.

## Q10. What is the conclusion of your project?
TradeIQ successfully demonstrates practical full-stack and ML integration. It is a strong academic implementation and can be scaled to production with planned enhancements.

## Q11. Why is PostgreSQL recommended instead of SQLite in production?
PostgreSQL provides better concurrency handling, reliability, and managed cloud support, while SQLite is limited for multi-user production workloads.

## Q12. How can the project be improved for industry readiness?
Add automated tests, monitoring/alerting, secure secret management, robust DevOps pipelines, and explainable AI output for prediction transparency.
