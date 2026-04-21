# Legal RAG Frontend 🎨

Modern Next.js frontend for the Legal RAG system with dark theme, real-time search, and beautiful visualizations.

---

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
cd frontend
npm install
```

### **2. Configure API Endpoint (Optional)**

Create `.env.local` if you want to change the API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### **3. Start Development Server**

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🎯 Features

### **✅ Implemented**

- ✅ **Document Upload** (drag & drop, PDF/DOCX/TXT)
- ✅ **Query Interface** (submit queries, view results)
- ✅ **Confidence Meter** (0-100 visual gauge)
- ✅ **Risk Badge** (color-coded: low/medium/high/critical)
- ✅ **Citation Display** (with verification status)
- ✅ **Counter-Arguments** (adversarial reasoning)
- ✅ **Document Management** (list, delete)
- ✅ **Dark Theme** (beautiful, modern UI)
- ✅ **Responsive Design** (mobile-friendly)
- ✅ **Real-time Stats** (system health, metrics)

---

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with navigation
│   ├── page.tsx           # Home/Dashboard page
│   ├── query/             # Query interface
│   ├── upload/            # Document upload
│   └── documents/         # Document management
│
├── components/            # Reusable UI components
│   ├── ConfidenceMeter.tsx
│   ├── RiskBadge.tsx
│   ├── CitationCard.tsx
│   └── CounterArgumentCard.tsx
│
├── lib/                   # Utilities
│   └── api.ts            # API client (Axios)
│
└── public/               # Static assets
```

---

## 🎨 Pages Overview

### **1. Home Page** (`/`)
- System status dashboard
- Quick action cards (Query, Upload, Documents)
- Feature highlights
- Real-time stats from backend

### **2. Query Page** (`/query`)
- Legal question input
- Jurisdiction selector
- Real-time results with:
  - Confidence meter (0-100)
  - Risk badge (low/medium/high/critical)
  - Answer with citations
  - Counter-arguments
  - Warnings
  - Assumptions & caveats

### **3. Upload Page** (`/upload`)
- Drag & drop file upload
- Document metadata input (ID, jurisdiction)
- Progress indicator
- Auto-redirect after success

### **4. Documents Page** (`/documents`)
- List all indexed documents
- View document details (chunks, jurisdiction)
- Delete documents
- Empty state for no documents

---

## 🔧 Configuration

### **Environment Variables**

Create `.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Optional: Analytics, etc.
```

### **Tailwind Colors**

Custom dark theme colors in `tailwind.config.ts`:

```typescript
colors: {
  'dark-bg': '#0f172a',      // Main background
  'dark-card': '#1e293b',    // Card background
  'dark-border': '#334155',  // Border color
}
```

---

## 🧪 Development

### **Run Dev Server**

```bash
npm run dev
```

### **Build for Production**

```bash
npm run build
npm start
```

### **Lint**

```bash
npm run lint
```

---

## 📡 API Integration

All API calls go through `lib/api.ts`:

```typescript
import { api } from '@/lib/api';

// Submit query
const result = await api.submitQuery({
  query: "What are the termination clauses?",
  jurisdiction: "California"
});

// Upload document
await api.uploadDocument(file, documentId, jurisdiction);

// Get documents
const docs = await api.getDocuments();

// Get stats
const stats = await api.getStats();
```

---

## 🎨 Component Usage

### **Confidence Meter**

```tsx
import { ConfidenceMeter } from '@/components/ConfidenceMeter';

<ConfidenceMeter score={85.5} label="Answer Confidence" />
```

### **Risk Badge**

```tsx
import { RiskBadge } from '@/components/RiskBadge';

<RiskBadge level="low" size="md" />
```

### **Citation Card**

```tsx
import { CitationCard } from '@/components/CitationCard';

<CitationCard 
  citation={{
    clause_id: "SECTION_7",
    quoted_text: "...",
    reasoning: "..."
  }}
  isValid={true}
  index={0}
/>
```

---

## 🚀 Deployment

### **Option 1: Vercel (Recommended)**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

### **Option 2: Docker**

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### **Option 3: Static Export**

```bash
# Add to next.config.js
output: 'export'

# Build
npm run build
# Output in ./out/
```

---

## 🎓 Key Design Decisions

### **Why Next.js App Router?**
- Modern React patterns (Server Components)
- File-based routing
- Built-in API routes (if needed)
- Excellent developer experience

### **Why Tailwind CSS?**
- Utility-first (rapid development)
- Dark theme support
- Tiny bundle size
- No CSS-in-JS runtime cost

### **Why Axios over Fetch?**
- Cleaner API
- Automatic JSON parsing
- Better error handling
- Timeout support (important for LLM calls)

### **Why TypeScript?**
- Type safety for API responses
- Better IDE support
- Catch errors at compile time
- Self-documenting code

---

## 🐛 Troubleshooting

### **"Failed to connect to backend"**

1. Check backend is running:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. Check CORS settings in `backend/src/api/main.py`

3. Verify API URL in `.env.local`

### **"Module not found"**

```bash
rm -rf node_modules package-lock.json
npm install
```

### **Build errors**

```bash
npm run lint
npm run build
```

---

## 📚 Resources

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript](https://www.typescriptlang.org/docs)
- [Axios](https://axios-http.com/docs/intro)

---

## 🎉 You're All Set!

Your Legal RAG frontend is ready! 🚀

Run both backend and frontend:

```bash
# Terminal 1 - Backend
cd backend
source ../legalRAG/bin/activate
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Then visit: **http://localhost:3000**
