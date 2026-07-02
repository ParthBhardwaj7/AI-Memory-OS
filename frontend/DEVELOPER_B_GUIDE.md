# Frontend Developer Guide (Developer B)

Welcome to the frontend team of **AI Memory OS**! You are responsible for creating a premium, responsive dark-themed Dashboard, file drop zones, chat assistants, timelines, and interactive knowledge graphs.

## 🚀 Commands You Need

First, navigate to the frontend directory:
```bash
cd frontend
```

### 1. Run Development Server
Runs the web app locally on [http://localhost:3000](http://localhost:3000).
```bash
npm run dev
```

### 2. Verify TypeScript Compilation (Run often)
Checks the project for syntax and Type errors without producing build files.
```bash
npx tsc --noEmit
```

### 3. Build for Production
Validates that the production package compiles successfully before submitting.
```bash
npm run build
```

---

## 🛠️ Your Core Responsibilities & How to Build Them

You will write your code inside the `src/` directory. The structure has already been initialized with skeletons and commented instructions.

### Task 1: Connect to Backend APIs (`src/lib/api.ts`)
We have pre-configured an Axios client. When Developer A runs the FastAPI server (normally at `http://localhost:8000`), the client is already mapped to it.
* You can import the API calls anywhere in your code like this:
  ```typescript
  import { memoryApi } from "@/lib/api";
  
  // Example call:
  const response = await memoryApi.queryMemory("When was my resume uploaded?");
  console.log(response.answer); // The LLM response
  console.log(response.sources); // List of document names used
  ```

### Task 2: Build Dashboard & Digests (`src/app/page.tsx`)
* **Goal**: Display stats cards and compile the daily summary.
* **To Do**:
  1. Retrieve overall memory counts (Total, PDFs, Images, Audio, URLs) and display them in the stat cards.
  2. Implement the **Generate Digest** button: when clicked, show a loading spinner and call `memoryApi.getDailyDigest()`, then render the response Markdown nicely.

### Task 3: Build Ingestion Upload Zones (`src/app/upload/page.tsx`)
* **Goal**: Build Drag & Drop upload states and URL inputs.
* **To Do**:
  1. We installed `react-dropzone`. When a file is dropped in the active tab (PDF, Image, or Audio), read it and call the corresponding upload API (e.g., `memoryApi.uploadPdf(file)`).
  2. Show a progress percentage or a loading message saying *"Uploading & Cognifying Memory..."* so the user knows the AI is indexing it.
  3. Validate forms and URLs.

### Task 4: Ask Your Memory Chat UI (`src/app/chat/page.tsx`)
* **Goal**: High-fidelity chat bubble interface with source references.
* **To Do**:
  1. Display user bubbles on the right (indigo background) and assistant bubbles on the left (dark background).
  2. Display the list of source references (e.g., `["Resume.pdf", "meeting_notes.wav"]`) under the assistant's answer as clickable pills.
  3. Implement smooth auto-scroll to the bottom of the message feed when a new answer arrives.

### Task 5: Memory Timeline (`src/app/timeline/page.tsx`)
* **Goal**: Chronological list of user logs.
* **To Do**:
  1. Call `memoryApi.getTimeline()`.
  2. Group events into periods (Today, Yesterday, Last Week).
  3. Render different card styling/icons depending on the memory type (PDF gets file icon, Audio gets headphone icon, URL gets link icon).

### Task 6: Knowledge Graph (`src/app/graph/page.tsx`)
* **Goal**: Render the Cognee graph nodes in a canvas.
* **To Do**:
  1. We installed `reactflow`. Load the nodes and edges on mount via `memoryApi.getGraph()`.
  2. Configure `reactflow` background grids and viewport zoom limits.
  3. Connect edge markers (arrows) so relations point from parent nodes to child nodes.

---

## 🎨 Styling Guidelines (Tailwind CSS)

To make this feel like a **premium product** that wows the judges:
1. **Dark Mode**: Use dark backgrounds (`bg-slate-950` or `bg-slate-900`) and glowing borders (`border-slate-800` or `border-indigo-500/20`).
2. **Gradients**: Use background gradients for headings and cards (e.g., `bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent`).
3. **Typography**: Keep text clear and utilize sizes strategically.
4. **Transitions**: Add hover transitions (`transition-all duration-200 hover:scale-105`) to interactive cards so the interface feels alive.
