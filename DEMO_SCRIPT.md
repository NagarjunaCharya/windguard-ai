# WindGuard AI MVP - Demo Script

## 🎯 Demo Overview
**Duration:** 3-4 minutes  
**Audience:** Envision/Innowhyte hackathon judges  
**Goal:** Demonstrate AI-powered predictive maintenance with adaptive learning capabilities

---

## 🚀 Pre-Demo Setup Checklist

### Backend (Terminal 1):
```powershell
cd C:\Users\Nagarjuna\OneDrive\Desktop\CYPHER_3.02\windguard-backend
.\venv\Scripts\Activate.ps1
python app.py
```
**Expected Output:** 
- `✓ BiLSTM model loaded successfully (135,297 parameters)`
- `🚀 WindGuard AI Backend Ready!`
- `Running on: http://localhost:5000`

### Frontend (Terminal 2):
```powershell
cd C:\Users\Nagarjuna\OneDrive\Desktop\CYPHER_3.02\windguard-frontend\production
python -m http.server 8080
```
**Expected Output:**
- `Serving HTTP on :: port 8080`

### Browser:
- Open: http://localhost:8080/windguard-dashboard.html
- Verify: Dashboard loads with turbine cards and metrics

---

## 📖 Demo Flow (3-4 minutes)

### 1. Introduction (30 seconds)
**Script:**
> "WindGuard AI is a predictive maintenance platform for wind farms that combines two key innovations:
> 
> **Envision Track:** AI-powered performance optimization using BiLSTM deep learning for 72-hour failure forecasting with 91% accuracy and 15% yaw optimization gains.
>
> **Innowhyte Track:** Adaptive learning companion with role-based explanations and AR-guided maintenance for field technicians.
>
> Let me walk you through the MVP."

**Action:** Show the main dashboard

---

### 2. Dashboard Overview (60 seconds)

**Script:**
> "The dashboard provides real-time monitoring of 5 wind turbines across our farm. Each card shows:"

**Point to elements:**
- **Turbine Cards:** "Live status, risk scores from our BiLSTM model, and current power output"
- **Turbine #2 (Warning):** "Notice Turbine #2 has a 65% failure risk - flagged in amber"
- **Model Metrics Panel:** "Our BiLSTM model achieves 91.3% accuracy, 95.4% AUC-ROC, and 84.2% precision"
- **Business Impact Panel:** "$521K in OPEX savings (20% reduction) and 15% performance gain through AI-optimized yaw angles"

**Action:** Hover over elements, show responsive design

---

### 3. Predictive Analytics Deep Dive (60 seconds)

**Script:**
> "Let's investigate Turbine #2's warning. I'll click 'Details' to see the AI prediction."

**Actions:**
1. Click "View Details" on Turbine #2
2. Read the alert message:
   - Risk: 65%
   - Status: WARNING
   - Explanation: Gearbox temperature anomaly (53.2% SHAP contribution)
   - Action: Schedule inspection within 72 hours

**Script:**
> "Our BiLSTM model analyzes 72 hours of sensor data across 4 features:
> - **Gearbox Temperature** (53.2% importance - the main issue here)
> - **Vibration** (30.8% importance)
> - **Wind Speed** (10.4%)
> - **Yaw Position** (5.6%)
>
> The model predicts this turbine has a 65% chance of failure in the next 72 hours if we don't intervene.
>
> This is **Envision's AI Performance** track - using deep learning to prevent costly downtime."

**Action:** Scroll to Risk Trend Chart

**Script:**
> "The chart shows the risk trajectory over the next 3 days. Without maintenance, risk climbs to 85% by hour 72."

---

### 4. Adaptive Learning - AR Maintenance Guide (45 seconds)

**Script:**
> "Now for **Innowhyte's Adaptive Learning** track. Let's see how we guide technicians through the repair."

**Actions:**
1. Click sidebar: "AR Guide"
2. Show AR Guide page

**Script:**
> "Our AR-guided maintenance provides role-based, step-by-step instructions:
> - **7 detailed steps** from safety checks to reassembly
> - **AR overlay mockup** - in production, this would show 3D models on tablet/headset
> - **Safety-first approach** with LOTO (lockout/tagout) procedures
> - **Estimated 45-60 minutes** with required tools listed
>
> This adapts to user expertise level - showing more detail for junior techs, streamlined for experts."

**Action:** Scroll through steps, highlight safety badge

---

### 5. Vendor Recommendations (30 seconds)

**Script:**
> "Finally, our AI matches the issue to certified vendors automatically."

**Actions:**
1. Click sidebar: "Vendors"
2. Show vendor cards

**Script:**
> "For gearbox issues, the system recommends:
> - **Siemens Energy** - 24h response, 4.8 rating, $12-18K
> - **Envision Partner** - 36h response, certified for our turbines
> - **Local Technician** - 12h response, on-site today
>
> One-click contact initiates the work order with all diagnostic data pre-filled."

**Action:** Hover over contact buttons

---

### 6. Impact Summary & Technical Details (30 seconds)

**Script:**
> "Let me summarize the business and technical impact:
>
> **Business Value:**
> - $521,700 annual OPEX savings (20% reduction)
> - 15% yaw optimization gain = +2.8 GWh energy
> - 35% downtime reduction through predictive maintenance
>
> **Technical Stack:**
> - **Model:** Bidirectional LSTM (135K parameters)
> - **Training:** 628 sequences, 72-hour windows
> - **Accuracy:** 91.27% with 84.21% precision
> - **Explainability:** SHAP values for transparency
> - **Frontend:** Bootstrap 5, Chart.js, custom dark theme
> - **Backend:** Flask API serving PyTorch predictions
> - **Deployment:** Production-ready with CI/CD pipeline
>
> This MVP demonstrates both tracks:
> 1. **Envision:** AI performance optimization with real ML models
> 2. **Innowhyte:** Adaptive learning with AR guidance and contextual help
>
> All code is on GitHub, fully documented, and ready to scale."

**Action:** Return to dashboard, refresh to show live data

---

## 🎬 Closing (10 seconds)

**Script:**
> "WindGuard AI - preventing failures before they happen, empowering technicians with AI, and maximizing renewable energy output. Thank you!"

**Action:** Show dashboard one final time

---

## 💡 Q&A Preparation

### Likely Questions:

**Q: "How accurate is your model in real-world scenarios?"**  
A: "91.27% accuracy on test set with 84.21% precision. We optimized threshold to 0.75 to minimize false positives - critical for production trust. In real deployment, we'd continuously retrain with site-specific data."

**Q: "What if the backend is offline?"**  
A: "The frontend gracefully degrades to mock data with error notifications. Designed for edge deployment where connectivity isn't guaranteed."

**Q: "How do you handle class imbalance (failures are rare)?"**  
A: "We use pos_weight=4.28 in our BCEWithLogitsLoss function and optimized the decision threshold to 0.75. This balances catching real failures vs. avoiding false alarms."

**Q: "Can this scale to hundreds of turbines?"**  
A: "Yes - the BiLSTM processes sequences independently, so it's horizontally scalable. For hundreds of turbines, we'd add:
- Database (PostgreSQL) instead of CSV
- Message queue (RabbitMQ) for async predictions
- Kubernetes for container orchestration
- Redis for caching frequent predictions"

**Q: "What about the GNN component mentioned in specs?"**  
A: "We implemented BiLSTM-only for MVP (as per fallback plan) since it meets all targets. GNN would add multi-turbine wake effect modeling - planned for v2 when we have spatial farm data."

**Q: "How does adaptive learning work?"**  
A: "Currently demonstrates role-based content (detailed for juniors, concise for experts). In production, we'd add:
- User proficiency tracking
- Learning curve analytics
- Personalized difficulty adjustment
- Integrated training modules"

**Q: "What about regulatory compliance (safety standards)?"**  
A: "AR guide enforces LOTO procedures and safety checks. In production, we'd integrate with:
- IEC 61508 (safety systems)
- ISO 13849 (machinery safety)
- OSHA regulations
- Digital signature for procedure completion"

---

## 🛠️ Troubleshooting

### Issue: Backend won't start
**Solution:**
```powershell
cd windguard-backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Issue: Frontend 404 errors
**Solution:** 
- Check you're in `/production` folder
- Files: `windguard-dashboard.html`, `ar-guide.html`, `vendors.html`

### Issue: CORS errors
**Solution:** 
- Flask has `CORS(app)` enabled
- Check browser console for specific errors
- Try: `flask run --host=0.0.0.0 --port=5000`

### Issue: Model not loading
**Solution:**
- Verify `bilstm_model.pth` exists in backend folder
- Check `model.py` is present
- Output should show: "✓ BiLSTM model loaded successfully"

---

## 📊 Demo Metrics to Emphasize

| Metric | Value | Impact |
|--------|-------|--------|
| Model Accuracy | 91.27% | Exceeds 85% target |
| Precision | 84.21% | Exceeds 80% target (optimized threshold) |
| AUC-ROC | 95.38% | Excellent discriminative ability |
| OPEX Savings | $521K | 20% cost reduction |
| Yaw Gain | +15% | +2.8 GWh annual energy |
| False Positive Rate | 2.4% | Minimizes unnecessary maintenance |
| Sequence Length | 72 hours | 3-day prediction window |
| Model Parameters | 135,297 | Lightweight, edge-deployable |

---

## 🎨 Visual Highlights

1. **Dark Theme:** Professional green/blue wind energy palette
2. **Risk Color Coding:** Green (safe), Amber (warning), Red (critical)
3. **Live Charts:** Chart.js line graph for risk trends
4. **Responsive Design:** Works on desktop, tablet, mobile
5. **AR Mockups:** Clear visualization of future AR capabilities
6. **Vendor Cards:** Professional presentation with ratings

---

## 🔗 Key URLs

- **Dashboard:** http://localhost:8080/windguard-dashboard.html
- **AR Guide:** http://localhost:8080/ar-guide.html
- **Vendors:** http://localhost:8080/vendors.html
- **Backend API:** http://localhost:5000/
- **API Health:** http://localhost:5000/health
- **API Turbines:** http://localhost:5000/api/turbines
- **API Predict:** http://localhost:5000/api/predict/2

---

## 📝 Post-Demo Notes

After demo, mention:
- GitHub repo: `https://github.com/NagarjunaCharya/windguard-ai`
- Branch: `phase2-model` (Phase 2 complete), `main` (production)
- Documentation: `PHASE2_COMPLETE.md` has full technical details
- Phase 1: Data ingestion (complete)
- Phase 2: ML modeling (complete)
- Phase 3: Dashboard integration (this MVP)

---

**Good luck with the demo! 🚀🌬️**
