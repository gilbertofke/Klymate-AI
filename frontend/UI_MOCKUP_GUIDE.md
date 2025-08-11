# 🎨 Klymate AI - UI Mockup Guide

**Visual Design Reference for Green & Sky Blue Theme**

---

## 🌈 **COLOR PALETTE VISUALIZATION**

### **Primary Colors**
```
🟢 Primary Green (#22C55E)    - Main action buttons, progress bars
🔵 Primary Blue (#0EA5E9)     - Secondary actions, info elements
🌿 Light Green (#86EFAC)      - Success states, positive feedback
💙 Light Blue (#7DD3FC)       - Info states, calm backgrounds
🌲 Dark Green (#15803D)       - Headers, important text
🌊 Dark Blue (#0369A1)        - Navigation, emphasis text
```

### **Background Gradients**
```css
/* Hero Section */
background: linear-gradient(135deg, #F0FDF4 0%, #F0F9FF 100%);

/* Cards */
background: linear-gradient(145deg, #DCFCE7 0%, #E0F2FE 100%);

/* Buttons */
background: linear-gradient(135deg, #22C55E 0%, #0EA5E9 100%);
```

---

## 📱 **KEY SCREEN LAYOUTS**

### **1. Welcome/Landing Screen**
```
┌─────────────────────────────────────┐
│  🌱 Klymate AI                     │
│                                     │
│     [Hero Image: Earth/Nature]     │
│                                     │
│  "Track Your Carbon Footprint      │
│   Make a Real Environmental        │
│   Impact"                          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │     Get Started (Green)     │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │     Sign In (Blue)          │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### **2. Dashboard (Main Hub)**
```
┌─────────────────────────────────────┐
│ ☰ Klymate AI            🔔 👤     │
├─────────────────────────────────────┤
│                                     │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ │🌍 8,240 │ │💚 1,250 │ │🔥 15    ││
│ │kg CO2   │ │kg Saved │ │Day      ││
│ │Current  │ │Total    │ │Streak   ││
│ └─────────┘ └─────────┘ └─────────┘│
│                                     │
│ ┌─────────────────────────────────┐ │
│ │     📊 Carbon Footprint        │ │
│ │     [Interactive Chart]        │ │
│ │     Baseline: 10,000 kg        │ │
│ │     Current:  8,240 kg (-18%)  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Quick Actions:                      │
│ 🚗 🥗 ⚡ 🛍️                        │
│                                     │
│ Recent Habits:                      │
│ • Biked to work (+2.5 kg saved)    │
│ • Plant-based lunch (+1.2 kg)      │
│ • Used renewable energy (+3.1 kg)  │
└─────────────────────────────────────┘
```

### **3. Habit Logging Interface**
```
┌─────────────────────────────────────┐
│ ← Log New Habit              ✓     │
├─────────────────────────────────────┤
│                                     │
│ Choose Category:                    │
│                                     │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ │   🚗    │ │   🥗    │ │   ⚡    ││
│ │Transport│ │  Diet   │ │ Energy  ││
│ └─────────┘ └─────────┘ └─────────┘│
│                                     │
│ ┌─────────┐                        │
│ │   🛍️    │                        │
│ │Lifestyle│                        │
│ └─────────┘                        │
│                                     │
│ Selected: Transport 🚗              │
│                                     │
│ What did you do?                    │
│ ┌─────────────────────────────────┐ │
│ │ Biked to work instead of car   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Distance: [____] km                 │
│                                     │
│ 💚 Estimated CO2 Saved: 2.5 kg     │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │        Log Habit (Green)        │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### **4. Onboarding Survey**
```
┌─────────────────────────────────────┐
│ ← Step 2 of 4: Transport           │
├─────────────────────────────────────┤
│ ████████░░░░ 50%                   │
│                                     │
│ 🚗 Tell us about your transport     │
│                                     │
│ How many km do you drive per week?  │
│ ┌─────────────────────────────────┐ │
│ │ [____] km                       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ How often do you use public         │
│ transport?                          │
│ ○ Daily   ○ Weekly   ○ Rarely      │
│                                     │
│ How many flights do you take        │
│ per year?                           │
│ ┌─────────────────────────────────┐ │
│ │ [____] flights                  │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────┐         ┌─────────────┐│
│ │  Back   │         │    Next     ││
│ │ (Gray)  │         │   (Green)   ││
│ └─────────┘         └─────────────┘│
└─────────────────────────────────────┘
```

### **5. Analytics/Insights Page**
```
┌─────────────────────────────────────┐
│ ← Your Carbon Insights              │
├─────────────────────────────────────┤
│                                     │
│ ┌─────────────────────────────────┐ │
│ │     📈 Monthly Trend            │ │
│ │     [Line Chart: Green Line]    │ │
│ │     Jan: 850kg → Dec: 720kg     │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │     🥧 Category Breakdown       │ │
│ │     [Pie Chart: Green/Blue]     │ │
│ │     Transport: 45%              │ │
│ │     Energy: 30%                 │ │
│ │     Diet: 15%                   │ │
│ │     Lifestyle: 10%              │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 💡 Recommendations:                 │
│ • Switch to renewable energy        │
│   (Save 200kg CO2/month)           │
│ • Try 2 plant-based meals/week     │
│   (Save 50kg CO2/month)            │
│                                     │
│ 🏆 Your Impact:                     │
│ • Equivalent to planting 15 trees  │
│ • Same as removing car for 2 weeks │
└─────────────────────────────────────┘
```

---

## 🎨 **COMPONENT DESIGN PATTERNS**

### **Cards with Gradients**
```css
.eco-card {
  background: linear-gradient(145deg, #DCFCE7 0%, #E0F2FE 100%);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.1);
}
```

### **Progress Indicators**
```css
.progress-ring {
  stroke: url(#greenGradient);
  stroke-width: 8;
  fill: transparent;
  transform-origin: center;
  animation: progressFill 1s ease-out;
}

.progress-bar {
  background: linear-gradient(90deg, #22C55E 0%, #0EA5E9 100%);
  height: 8px;
  border-radius: 4px;
  transition: width 0.5s ease;
}
```

### **Action Buttons**
```css
.primary-button {
  background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  box-shadow: 0 4px 14px 0 rgba(34, 197, 94, 0.3);
  transition: all 0.2s ease;
}

.primary-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px 0 rgba(34, 197, 94, 0.4);
}

.secondary-button {
  background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
  /* Similar styling with blue gradient */
}
```

---

## 🌟 **MICRO-INTERACTIONS**

### **Habit Logging Success**
```
1. User taps "Log Habit"
2. Button shows loading spinner (green)
3. Success animation: ✓ checkmark with green pulse
4. CO2 counter animates up: +2.5kg saved
5. Confetti animation with green/blue particles
6. Toast notification: "Great job! 🌱"
```

### **Streak Counter**
```
1. Daily habit logged
2. Streak number increments with bounce animation
3. Fire emoji pulses with orange glow
4. If milestone (7, 30, 100 days):
   - Badge unlock animation
   - Celebration modal with achievement
```

### **Carbon Footprint Reduction**
```
1. New data loads
2. Chart line animates from old to new position
3. Percentage change highlights with green color
4. Tree/leaf icons animate growing
5. Impact comparison updates with smooth transition
```

---

## 📐 **RESPONSIVE DESIGN BREAKPOINTS**

### **Mobile (320px - 768px)**
```css
/* Stack cards vertically */
.dashboard-grid {
  grid-template-columns: 1fr;
  gap: 16px;
}

/* Bottom navigation */
.mobile-nav {
  position: fixed;
  bottom: 0;
  background: white;
  border-top: 1px solid #E5E7EB;
}

/* Touch-friendly buttons */
.touch-button {
  min-height: 44px;
  min-width: 44px;
}
```

### **Tablet (768px - 1024px)**
```css
/* 2-column layout */
.dashboard-grid {
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* Side navigation */
.tablet-nav {
  position: fixed;
  left: 0;
  width: 240px;
}
```

### **Desktop (1024px+)**
```css
/* 3-column layout */
.dashboard-grid {
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
}

/* Full sidebar */
.desktop-nav {
  width: 280px;
}
```

---

## 🎯 **ACCESSIBILITY FEATURES**

### **Color Contrast**
```css
/* Ensure WCAG AA compliance */
.text-primary { color: #15803D; } /* 4.5:1 ratio on white */
.text-secondary { color: #0369A1; } /* 4.5:1 ratio on white */
.text-muted { color: #6B7280; } /* 4.5:1 ratio on white */
```

### **Focus States**
```css
.focusable:focus {
  outline: 2px solid #22C55E;
  outline-offset: 2px;
  border-radius: 4px;
}
```

### **Screen Reader Support**
```html
<!-- Semantic HTML -->
<main aria-label="Dashboard">
  <section aria-labelledby="carbon-stats">
    <h2 id="carbon-stats">Carbon Footprint Statistics</h2>
    <!-- Content -->
  </section>
</main>

<!-- ARIA labels -->
<button aria-label="Log new habit" aria-describedby="habit-help">
  <span aria-hidden="true">+</span>
</button>
<div id="habit-help" class="sr-only">
  Click to log a new eco-friendly habit
</div>
```

---

## 🚀 **ANIMATION LIBRARY**

### **Page Transitions**
```css
.page-enter {
  opacity: 0;
  transform: translateX(100%);
}

.page-enter-active {
  opacity: 1;
  transform: translateX(0);
  transition: all 300ms ease-out;
}

.page-exit {
  opacity: 1;
  transform: translateX(0);
}

.page-exit-active {
  opacity: 0;
  transform: translateX(-100%);
  transition: all 300ms ease-in;
}
```

### **Loading States**
```css
.skeleton {
  background: linear-gradient(90deg, #F3F4F6 25%, #E5E7EB 50%, #F3F4F6 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## 💡 **DESIGN PRINCIPLES**

### **Environmental Psychology**
- **Green = Growth, Success, Positive Impact**
- **Blue = Trust, Calm, Clean Environment**
- **Organic Shapes = Natural, Sustainable**
- **Smooth Animations = Effortless Experience**

### **User Engagement**
- **Immediate Feedback**: Every action shows instant result
- **Progress Visualization**: Clear progress toward goals
- **Gamification**: Points, badges, streaks, leaderboards
- **Social Proof**: Community impact and comparisons

### **Information Hierarchy**
- **Primary**: Current carbon footprint (largest, green)
- **Secondary**: CO2 saved, streak (medium, blue/green)
- **Tertiary**: Detailed stats, history (smaller, gray)

---

This mockup guide provides a comprehensive visual reference for implementing the green and sky blue theme across all components of the Klymate AI frontend. The design emphasizes environmental consciousness while maintaining modern usability standards.

**Ready to create a beautiful, engaging eco-friendly app! 🌱✨**